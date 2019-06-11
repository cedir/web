# -*- coding: utf-8 -*-
import datetime

from pyafipws.wsaa import WSAA
from pyafipws.wsmtx import WSMTXCA
from xml.parsers.expat import ExpatError
from httplib2 import ServerNotFoundError

class AfipError(RuntimeError):
    pass

class AfipErrorValidacion(AfipError):
    pass

class AfipErrorRed(AfipError):
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
        self.ws = WSMTXCA()
        self.ws.LanzarExcepciones = True
        
        # datos de conexión (cambiar URL para producción)
        # Esa URL tambien cambia si cambias de WSMTXCA a WSFEv1
        cache = None
        wsdl = "https://fwshomo.afip.gov.ar/wsmtxca/services/MTXCAService?wsdl"
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
        # Pide un ticket de acceso a la AFIP que sera usado en todas las requests.
        self.ta = self.wsaa.Autenticar("wsmtxca", self.cert, self.clave, self.wsaa_url, debug=True)
        if not self.ta:
            raise AfipError("Error WSAA: %s" % WSAA.Excepcion)

        # establecer credenciales (token y sign):
        self.ws.SetTicketAcceso(self.ta)
    
    @requiere_ticket
    def emitir_comprobante(self, lineas, iva, comprobantes_asociados, **kwargs):
        '''
        Emite un comprobante en la afip.
        Los argumentos son:
            Una lista de diccionarios linea
            Un diccionario con los parametros de iva
            Una lista de diccionarios que identifican cada uno a un comprobante asociado
            El resto de los argumentos se pasan como parametros en la request a la AFIP.
        Devuelve un diccionario con toda la info sobre el comprobante que nos devuelve la AFIP en caso de exito.
        Lanza AfipErrorRed en caso de error de conexion o si la la AFIP esta caida.
        Lanza AfipErrorValidacion en caso de fallar una validacion de datos.

        Por defecto, le pone:
            Fecha de hoy
            Concepto servicios
        '''
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        comprobante = {
            "concepto": 2, # Servicios
            "fecha_cbte": fecha,
            "fecha_venc_pago":  fecha,
            "fecha_serv_desde": fecha,
            "fecha_serv_hasta": fecha,
            "imp_trib": "0.00",         # Importe total otros tributos
            "imp_tot_conc": "0.00",     # Importe total conceptos no gravados
            "moneda_id": 'PES',         # La moneda es pesos argentinos.
            "moneda_ctz": '1.000'
        }
        # Creamos una factura desde una template y le actualizamos los valores especificados. 
        comprobante.update(kwargs)
        nro = long(self.ws.CompUltimoAutorizado(comprobante["tipo_cbte"], comprobante["punto_vta"]) or 0) + 1
        comprobante["cbte_desde"] = nro
        comprobante["cbt_hasta"] = nro
        self.ws.CrearFactura(**comprobante)

        # Agregar el IVA
        if iva:
            self.ws.AgregarIva(**iva)

        # Agregar las lineas
        for linea in lineas:
            self.ws.AgregarItem(**linea)

        # Si hay comprobantes asociados, los agregamos.
        for c in comprobantes_asociados:
            self.ws.AgregarCmpAsoc(c)

        # llamar al webservice de AFIP para autorizar la factura y obtener CAE:
        try:
            self.ws.CAESolicitar()
        except (ExpatError, ServerNotFoundError) as e:
            raise AfipErrorRed("Error de red emitiendo el comprobante.")
        if self.ws.Resultado == "R":
            # Si la AFIP nos rechaza el comprobante, lanzamos excepcion.
            raise AfipErrorValidacion(self.ws.ErrMsg)
        if self.ws.Resultado == "O":
            # Si hay observaciones (en self.ws.Obs), deberiamos logearlas en la DB.
            pass

        return {
            "cae": self.ws.CAE,
            "vencimiento": self.ws.Vencimiento,
            "numero": nro
        }

    @requiere_ticket
    def consultar_comprobante(self, codigo_afip_tipo, nro_terminal, cbte_nro):
        self.ws.ConsultarComprobante(codigo_afip_tipo, nro_terminal, cbte_nro)
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

