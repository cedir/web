# -*- coding: utf-8 -*-
'''
Modulo encargado de la comunicacion con el Webservice de la AFIP.
'''
from datetime import datetime
from xml.parsers.expat import ExpatError
from httplib2 import ServerNotFoundError

from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1

from comprobante.models import Comprobante
from settings import AFIP_WSAA_URL, AFIP_WSDL_URL, \
    CEDIR_CERT_PATH, CEDIR_PV_PATH, CEDIR_CUIT, BRUNETTI_CERT_PATH, BRUNETTI_PV_PATH, BRUNETTI_CUIT

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
    Esta clase redirige a la instancia indicada de _Afip segun si el comprobante
    es de Cedir o de Brunetti.
    '''
    def __init__(self):
        self.afip_cedir = _Afip(CEDIR_PV_PATH, CEDIR_CERT_PATH, CEDIR_CUIT)
        self.afip_brunetti = _Afip(BRUNETTI_PV_PATH, BRUNETTI_CERT_PATH, BRUNETTI_CUIT)
    def emitir_comprobante(self, comprobante_cedir, lineas):
        if comprobante_cedir.responsable == "Cedir":
            return self.afip_cedir.emitir_comprobante(comprobante_cedir, lineas)
        else:
            return self.afip_brunetti.emitir_comprobante(comprobante_cedir, lineas)
    def consultar_comprobante(self, comprobante_cedir):
        if comprobante_cedir.responsable == "Cedir":
            return self.afip_cedir.consultar_comprobante(comprobante_cedir)
        else:
            return self.afip_brunetti.consultar_comprobante(comprobante_cedir)
    def consultar_proximo_numero(self, responsable, nro_terminal, tipo_comprobante, subtipo):
        if responsable == "Cedir":
            return self.afip_cedir.consultar_proximo_numero(nro_terminal, tipo_comprobante, subtipo)
        else:
            return self.afip_brunetti.consultar_proximo_numero(nro_terminal, tipo_comprobante, subtipo)


class _Afip(object):
    '''
    Clase que abstrae la emision de comprobantes electronicos en la afip.
    '''
    def __init__(self, privada, certificado, cuit):
        # instanciar el componente para factura electrónica mercado interno
        self.webservice = WSFEv1()
        self.webservice.LanzarExcepciones = True

        # datos de conexión (cambiar URL para producción)
        cache = None
        wsdl = AFIP_WSDL_URL
        proxy = ""
        wrapper = ""
        cacert = None

        # conectar
        try:
            self.webservice.Conectar(cache, wsdl, proxy, wrapper, cacert)
        except (ExpatError, ServerNotFoundError):
            raise AfipErrorRed("Error en la conexion inicial con la AFIP.")

        self.cert = certificado       # archivos a tramitar previamente ante AFIP
        self.clave = privada
        self.wsaa_url = AFIP_WSAA_URL
        self.wsaa = WSAA()
        self.autenticar()

        self.webservice.Cuit = cuit

    def autenticar(self):
        '''
        Pide un ticket de acceso a la AFIP que sera usado en todas las requests.
        '''
        self.ticket_autenticacion = self.wsaa.Autenticar(
            "wsfe", self.cert, self.clave, self.wsaa_url, debug=True)
        if not self.ticket_autenticacion and self.wsaa.Excepcion:
            raise AfipError("Error WSAA: %s" % self.wsaa.Excepcion)

        # establecer credenciales (token y sign):
        self.webservice.SetTicketAcceso(self.ticket_autenticacion)

    @requiere_ticket
    def emitir_comprobante(self, comprobante_cedir, lineas):
        '''
        Toma un comprobante nuestro y una lista de lineas, lo traduce al formato que usa la AFIP en su webservice
        y trata de emitirlo.
        En caso de exito, setea las propiedades faltantes del comprobante que son dependientes
        de la AFIP.
        En caso de error, levanta una excepcion.
        '''
        nro = long(self.webservice.CompUltimoAutorizado(
            comprobante_cedir.codigo_afip, comprobante_cedir.nro_terminal) or 0) + 1
        fecha = datetime.now().strftime("%Y%m%d")
        imp_iva = sum([l.iva for l in lineas])
        if comprobante_cedir.gravado.id == IVA_EXCENTO:
            imp_neto = "0.00"
            imp_op_ex = sum([l.importe_neto for l in lineas])
        else:
            # importe neto gravado (todas las alicuotas)
            imp_neto = sum([l.importe_neto for l in lineas])
            imp_op_ex = "0.00"        # importe total operaciones exentas

        self.webservice.CrearFactura(
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
            self.webservice.AgregarIva(id_iva=4, base_imp=imp_neto, importe=imp_iva)
        elif comprobante_cedir.gravado.id == IVA_21:
            self.webservice.AgregarIva(id_iva=5, base_imp=imp_neto, importe=imp_iva)

        # Si hay comprobantes asociados, los agregamos.
        if comprobante_cedir.tipo_comprobante.id in [NOTA_DE_DEBITO, NOTA_DE_CREDITO] and comprobante_cedir.factura:
            comprobante_asociado = Comprobante.objects.get(
                id=comprobante_cedir.factura.id)
            self.webservice.AgregarCmpAsoc(
                tipo=comprobante_asociado.codigo_afip,
                pto_vta=comprobante_asociado.nro_terminal,
                nro=comprobante_asociado.numero)

        # llamar al webservice de AFIP para autorizar la factura y obtener CAE:
        try:
            self.webservice.CAESolicitar()
        except (ExpatError, ServerNotFoundError):
            raise AfipErrorRed("Error de red emitiendo el comprobante.")
        if self.webservice.Resultado == "R":
            # Si la AFIP nos rechaza el comprobante, lanzamos excepcion.
            raise AfipErrorValidacion(self.webservice.ErrMsg or self.webservice.Obs)
        if self.webservice.Resultado == "O":
            # Si hay observaciones (en self.webservice.Obs), deberiamos logearlas en la DB.
            pass

        comprobante_cedir.cae = self.webservice.CAE
        comprobante_cedir.vencimiento_cae = datetime.strptime(self.webservice.Vencimiento,'%Y%m%d')
        comprobante_cedir.numero = nro

    @requiere_ticket
    def consultar_comprobante(self, comprobante):
        '''
        Consulta que informacion tiene la AFIP sobre un comprobante nuestro dado su tipo,
        terminal y numero.
        Devuelve un diccionario con todos los datos.
        '''
        codigo_afip_tipo = comprobante.codigo_afip
        nro_terminal = comprobante.nro_terminal
        cbte_nro = comprobante.numero
        self.webservice.CompConsultar(codigo_afip_tipo, nro_terminal, cbte_nro)
        # Todos estos datos se setean en el objeto afip cuando la llamada a ConsultarComprobante es exitosa.
        # Notar que si falla (comprobante invalido, conexion...) queda con valores viejos!
        return {
            "fecha": self.webservice.FechaCbte,
            "numero": self.webservice.CbteNro,
            "punto_venta": self.webservice.PuntoVenta,
            "vencimiento": self.webservice.Vencimiento,
            "importe_total": self.webservice.ImpTotal,
            "CAE": self.webservice.CAE,
            "emision_tipo": self.webservice.EmisionTipo
        }

    @requiere_ticket
    def consultar_proximo_numero(self, nro_terminal, tipo_comprobante, subtipo):
        conversion = {
            'A': {1: 1, 3: 2, 4: 3},
            'B': {1: 6, 3: 7, 4: 8}
        }
        return long(self.webservice.CompUltimoAutorizado(conversion[subtipo][tipo_comprobante.id], nro_terminal) or 0)
