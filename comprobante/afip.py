# -*- coding: utf-8 -*-
'''
Modulo encargado de la comunicacion con el Webservice de la AFIP.
'''
import datetime
from xml.parsers.expat import ExpatError
from httplib2 import ServerNotFoundError

from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1

from comprobante.models import Comprobante, LineaDeComprobante

IVA_EXCENTO = 1
IVA_10_5 = 2
IVA_21 = 3

NOTA_DE_DEBITO = 3
NOTA_DE_CREDITO = 4

class AfipError(RuntimeError):
    '''
    Excepcion base para todos los errores relacionados a la AFIP.
    '''
    pass


class AfipErrorValidacion(AfipError):
    '''
    La afip rechazo un comprobante por fallar las validaciones.
    '''
    pass


class AfipErrorRed(AfipError):
    '''
    Ocurrio un error en la conexion con la AFIP.
    '''
    pass


def requiere_ticket(func):
    '''
    Decorador para que los metodos primero chequeen que el ticket no este vencido
    Y en caso de estarlo, lo renueven antes de hacer sus tareas.
    '''

    def wrapper(self, *args, **kwargs):
        if self.wsaa.Expirado():
            self.autenticar()
        return func(self, *args, **kwargs)
    return wrapper


class Afip(object):
    '''
    Clase que abstrae la emision de comprobantes electronicos en la afip.
    '''

    def __init__(self, privada, certificado, cuit):
        # instanciar el componente para factura electrónica mercado interno
        self.ws = WSFEv1()
        self.ws.LanzarExcepciones = True

        # datos de conexión (cambiar URL para producción)
        cache = None
        wsdl = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
        proxy = ""
        wrapper = ""
        cacert = None

        # conectar
        try:
            self.ws.Conectar(cache, wsdl, proxy, wrapper, cacert)
        except (ExpatError, ServerNotFoundError):
            raise AfipErrorRed("Error en la conexion inicial con la AFIP.")

        self.cert = certificado       # archivos a tramitar previamente ante AFIP
        self.clave = privada
        self.wsaa_url = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
        self.wsaa = WSAA()
        self.autenticar()

        self.ws.Cuit = cuit

    def autenticar(self):
        '''
        Pide un ticket de acceso a la AFIP que sera usado en todas las requests.
        '''
        self.ta = self.wsaa.Autenticar(
            "wsfe", self.cert, self.clave, self.wsaa_url, debug=True)
        if not self.ta and self.wsaa.Excepcion:
            raise AfipError("Error WSAA: %s" % self.wsaa.Excepcion)

        # establecer credenciales (token y sign):
        self.ws.SetTicketAcceso(self.ta)

    @requiere_ticket
    def emitir_comprobante(self, comprobante_cedir):
        '''
        Toma un comprobante nuestro, lo traduce al formato que usa la AFIP en su webservice
        y trata de emitirlo.
        En caso de exito, setea las propiedades faltantes del comprobante que son dependientes
        de la AFIP.
        En caso de error, levanta una excepcion.
        '''
        lineas = LineaDeComprobante.objects.filter(
            comprobante=comprobante_cedir.id)
        nro = long(self.ws.CompUltimoAutorizado(
            comprobante_cedir.codigo_afip, comprobante_cedir.nro_terminal) or 0) + 1
        fecha = datetime.datetime.now().strftime("%Y%m%d")
        imp_iva = sum([l.iva for l in lineas])
        if comprobante_cedir.gravado.id == IVA_EXCENTO:
            imp_neto = "0.00"
            imp_op_ex = sum([l.importe_neto for l in lineas])
        else:
            # importe neto gravado (todas las alicuotas)
            imp_neto = sum([l.importe_neto for l in lineas])
            imp_op_ex = "0.00"        # importe total operaciones exentas

        self.ws.CrearFactura(
            concepto=2,  # 2 es servicios, lo unico que hace el cedir.
            tipo_doc=comprobante_cedir.tipo_id_afip,
            nro_doc=comprobante_cedir.nro_id_afip,
            tipo_cbte=comprobante_cedir.codigo_afip,
            punto_vta=comprobante_cedir.nro_terminal,
            cbt_desde=nro,
            cbt_hasta=nro,
            imp_total=comprobante_cedir.total_facturado,
            imp_neto=imp_neto,
            imp_iva=imp_iva,
            imp_op_ex=imp_op_ex,
            fecha_cbte=fecha, # Estas fechas no cambian nunca, pero son requisito para el concepto=2
            fecha_serv_desde=fecha,
            fecha_serv_hasta=fecha,
            fecha_venc_pago=fecha)

        # Agregar el IVA
        if comprobante_cedir.gravado.id == IVA_10_5:
            self.ws.AgregarIva(id_iva=4, base_imp=imp_neto, importe=imp_iva)
        elif comprobante_cedir.gravado.id == IVA_21:
            self.ws.AgregarIva(id_iva=5, base_imp=imp_neto, importe=imp_iva)

        # Si hay comprobantes asociados, los agregamos.
        if comprobante_cedir.tipo_comprobante.id in [NOTA_DE_DEBITO, NOTA_DE_CREDITO] and comprobante_cedir.factura:
            comprobante_asociado = Comprobante.objects.get(
                id=comprobante_cedir.factura.id)
            self.ws.AgregarCmpAsoc(
                tipo=comprobante_asociado.codigo_afip,
                pto_vta=comprobante_asociado.nro_terminal,
                nro=comprobante_asociado.numero)

        # llamar al webservice de AFIP para autorizar la factura y obtener CAE:
        try:
            self.ws.CAESolicitar()
        except (ExpatError, ServerNotFoundError):
            raise AfipErrorRed("Error de red emitiendo el comprobante.")
        if self.ws.Resultado == "R":
            # Si la AFIP nos rechaza el comprobante, lanzamos excepcion.
            raise AfipErrorValidacion(self.ws.ErrMsg)
        if self.ws.Resultado == "O":
            # Si hay observaciones (en self.ws.Obs), deberiamos logearlas en la DB.
            pass

        comprobante_cedir.cae = self.ws.CAE
        comprobante_cedir.vencimiento_cae  = self.ws.Vencimiento
        comprobante_cedir.numero = nro

    @requiere_ticket
    def consultar_comprobante(self, codigo_afip_tipo, nro_terminal, cbte_nro):
        '''
        Consulta que informacion tiene la AFIP sobre un comprobante nuestro dado su tipo,
        terminal y numero.
        Devuelve un diccionario con todos los datos.
        '''
        self.ws.CompConsultar(codigo_afip_tipo, nro_terminal, cbte_nro)
        # Todos estos datos se setean en el objeto afip cuando la llamada a ConsultarComprobante es exitosa.
        # Notar que si falla (comprobante invalido, conexion...) queda con valores viejos!
        return {
            "fecha": self.ws.FechaCbte,
            "numero": self.ws.CbteNro,
            "punto_venta": self.ws.PuntoVenta,
            "vencimiento": self.ws.Vencimiento,
            "importe_total": self.ws.ImpTotal,
            "CAE": self.ws.CAE,
            "emision_tipo": self.ws.EmisionTipo
        }
