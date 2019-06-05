import datetime

from pyafipws.wsaa import WSAA
from pyafipws.wsmtx import WSMTXCA
from xml.parsers.expat import ExpatError

class AfipError(RuntimeError):
    pass

# Vamos a necesitar una instancia para Cedir y una para Brunetti!!!
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
            ok = self.ws.Conectar(cache, wsdl, proxy, wrapper, cacert)
        except ExpatError:
            raise AfipError("Error: parece que el servicio de la AFIP esta caido.")
        if not ok:
            raise AfipError("Error afip: %s" % WSAA.Excepcion)

        self.cert = certificado       # archivos a tramitar previamente ante AFIP 
        self.clave = privada
        self.wsaa_url = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
        self.wsaa = WSAA()
        self.autorizar()
        
        self.ws.Cuit = cuit

    def autenticar(self):
        # Pide un ticket de acceso a la AFIP que sera usado en todas las requests.
        self.ta = wsaa.Autenticar("wsmtxca", self.cert, self.clave, self.wsaa_url, debug=True)
        if not self.ta:
            raise RuntimeError("Error WSAA: %s" % WSAA.Excepcion)

        # establecer credenciales (token y sign) y cuit emisor:
        self.ws.SetTicketAcceso(self.ta)

    def comprobante_vacio(self):
        # Usamos por defecto la fecha actual
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        return {
            fecha_cbte: fecha,
            fecha_venc_pago:  fecha,
            fecha_serv_desde: fecha,
            fecha_serv_hasta: fecha,
            imp_trib: "0.00",         # Importe total otros tributos
            imp_tot_conc: "0.00",     # Importe total conceptos no gravados
            moneda_id: 'PES',         # La moneda es pesos argentinos.
            moneda_ctz: '1.000'
        }
    
    @requiere_ticket
    def emitir_comprobante(self, **kwargs):
        comprobante = self.comprobante_vacio()

        # meter los argumentos en el comprobante, pisando valores si hace falta.
        pass

        self.ws.CrearFactura(comprobante)

        # Agregar el IVA
        pass

        # Agregar las lineas
        pass

        # llamar al webservice de AFIP para autorizar la factura y obtener CAE:
        self.ws.CAESolicitar()

        # datos devueltos por AFIP:
        return {
            "resultado": self.ws.Resultado,
            "reproceso": self.ws.Reproceso,
            "cae": self.ws.CAE,
            "vencimiento": self.ws.Vencimiento,
            "mensaje_error_afip": self.ws.ErrMsg,
            "mensaje_obs_afip": self.ws.Obs,
            "numero": cbte_nro + 1
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


def requiere_ticket(func):
    # Decorador para que los metodos primero chequeen que el ticket no este vencido
    def wrapper(self, **kwargs):
        if self.wsaa.Expirado():
            self.autenticar()
        return func(self, **kwargs)