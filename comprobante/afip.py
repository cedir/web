# -*- coding: utf-8 -*-
'''
Modulo encargado de la comunicacion con el Webservice de la AFIP.
'''
from datetime import date, datetime, timedelta
from xml.parsers.expat import ExpatError
from httplib2 import ServerNotFoundError

from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1

from comprobante.models import Comprobante, ID_TIPO_COMPROBANTE_FACTURA, \
    ID_TIPO_COMPROBANTE_LIQUIDACION, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA
from settings import AFIP_WSAA_URL, AFIP_WSDL_URL, \
    CEDIR_CERT_PATH, CEDIR_PV_PATH, CEDIR_CUIT, BRUNETTI_CERT_PATH, BRUNETTI_PV_PATH, BRUNETTI_CUIT

IVA_EXCENTO = 1
IVA_10_5 = 2
IVA_21 = 3

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
        nro = self.consultar_proximo_numero(comprobante_cedir.nro_terminal, comprobante_cedir.tipo_comprobante, comprobante_cedir.sub_tipo)
        fecha = comprobante_cedir.fecha_emision.strftime("%Y%m%d")
        # En estos tipos de comprobante en especifico, la AFIP te prohibe poner un campo fecha de vencimiento.
        fecha_vto = None if comprobante_cedir.tipo_comprobante.id in [ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA] else comprobante_cedir.fecha_vencimiento.strftime("%Y%m%d")
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
            fecha_cbte=fecha, # Estas fechas no cambian nunca, pero son requisito de la AFIP para el concepto=2
            fecha_serv_desde=fecha,
            fecha_serv_hasta=fecha,
            fecha_venc_pago=fecha_vto)

        # Agregar el IVA
        if comprobante_cedir.gravado.id == IVA_10_5:
            self.webservice.AgregarIva(id_iva=4, base_imp=imp_neto, importe=imp_iva)
        elif comprobante_cedir.gravado.id == IVA_21:
            self.webservice.AgregarIva(id_iva=5, base_imp=imp_neto, importe=imp_iva)

        # Si hay comprobantes asociados, los agregamos.
        if comprobante_cedir.tipo_comprobante.id in [
            ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, # Para comprobantes no electronicos puede no ser necesario pero se los deja por completitud
            ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO,
            ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA,
            ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA] and comprobante_cedir.factura:
            comprobante_asociado = comprobante_cedir.factura
            self.webservice.AgregarCmpAsoc(
                tipo=comprobante_asociado.codigo_afip,
                pto_vta=comprobante_asociado.nro_terminal,
                nro=comprobante_asociado.numero,
                cuit=self.webservice.Cuit, # Cuit emisor.
                fecha=comprobante_asociado.fecha_emision.strftime("%Y%m%d")
            )

        # Si es Factura de Credito Electronica, hayq eu agregar como opcional el CBU del Cedir
        if comprobante_cedir.tipo_comprobante.id in [
            ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA]:
            self.webservice.AgregarOpcional(2101, "0150506102000109564632")

        # Si es Nota de Debito/Credito Electronica, hay que agregar un opcional indicando que no es anulacion.
        # En principio, el Cedir nunca anula facturas.
        if comprobante_cedir.tipo_comprobante.id in [
            ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA,
            ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA]:
            self.webservice.AgregarOpcional(22, "N")

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
        comprobante_cedir.vencimiento_cae = datetime.strptime(self.webservice.Vencimiento,'%Y%m%d').date()
        comprobante_cedir.numero = nro

    @requiere_ticket
    def consultar_comprobante(self, comprobante):
        '''
        Consulta que informacion tiene la AFIP sobre un comprobante nuestro.
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
    def consultar_proximo_numero(self, nro_terminal, tipo_comprobante, sub_tipo):
        codigo_afip = Comprobante(nro_terminal=nro_terminal, tipo_comprobante=tipo_comprobante, sub_tipo=sub_tipo).codigo_afip
        return long(self.webservice.CompUltimoAutorizado(codigo_afip, nro_terminal) or 0) + 1
