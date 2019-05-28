#!/usr/bin/python
# -*- coding: utf8 -*-

#################################################################################
#
# Prueba de concepto de emision de comprobantes con al API de la AFIP
# Llamar con:
# python poc_afip.py path_archivo_clave_privada path_archivo_certificado numero_cuit
# Claramente los archivos tienen que ser del entorno de homologacion.
#
#####################################################################################



# importar modulos python
import datetime
import os,sys,inspect

# Correccion del path para importar desde el directorio padre
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import wsgi # Importar esto hace lo del setting e iniciar django
from comprobante.models import Comprobante, LineaDeComprobante

# importar componentes del módulo PyAfipWs
from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1



class Facturador(object):
    def __init__(self, privada, certificado, cuit):
        # instanciar el componente para factura electrónica mercado interno
        self.wsfev1 = WSFEv1()
        self.wsfev1.LanzarExcepciones = True
        
        # datos de conexión (cambiar URL para producción)
        cache = None
        wsdl = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
        proxy = ""
        wrapper = ""    # "pycurl" para usar proxy avanzado / propietarios
        # datos de la factura de prueba (encabezado):
        cacert = None   # "afip_ca_info.crt" para verificar canal seguro

        # conectar
        ok = self.wsfev1.Conectar(cache, wsdl, proxy, wrapper, cacert)
        if not ok:
            raise RuntimeError("Error WSFEv1: %s" % WSAA.Excepcion)


        # autenticarse frente a AFIP (obtención de ticket de acceso):
        cert = certificado       # archivos a tramitar previamente ante AFIP 
        clave = privada     # (ver manual)
        wsaa_url = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
        self.ta = WSAA().Autenticar("wsfe", cert, clave, wsaa_url, debug=True)
        if not self.ta:
            raise RuntimeError("Error WSAA: %s" % WSAA.Excepcion)

        # establecer credenciales (token y sign) y cuit emisor:
        self.wsfev1.SetTicketAcceso(self.ta)
        self.wsfev1.Cuit = cuit

    def emitir_en_afip(self, comprobante_cedir):
        lineas = LineaDeComprobante.objects.filter(comprobante = comprobante_cedir.id)

        
        # Habria que usar la fecha del comprobante, pero la API me limita a facturar cerca de la fecha actual.
        # fecha = comprobante_cedir.fecha_emision.strftime("%Y%m%d")
        fecha = datetime.datetime.now().strftime("%Y%m%d")
        fecha_cbte = fecha
        fecha_venc_pago = fecha
        # Fechas del período del servicio facturado
        fecha_serv_desde = fecha
        fecha_serv_hasta = fecha

        # Todo esto ya lo tenemos en el comprobante.
        tipo_cbte = comprobante_cedir.codigo_afip
        punto_vta = comprobante_cedir.nro_terminal
        imp_total = comprobante_cedir.total_facturado
        tipo_doc = comprobante_cedir.tipo_id_afip
        nro_doc = comprobante_cedir.nro_id_afip
        imp_neto = sum([l.importe_neto for l in lineas])       # importe neto gravado (todas las alicuotas)
        imp_iva = sum([l.iva for l in lineas])        # importe total iva liquidado (idem)
        concepto = 2 # Servicios, lo unico que hace el CEDIR.


        #Si es nota, hay que agregar el comprobante asociado.

        # En realidad habria que usar el numero del comprobante, pero con este certificado no puedo.
        cbte_nro = long(self.wsfev1.CompUltimoAutorizado(tipo_cbte, punto_vta) or 0)

        cbt_desde = cbte_nro + 1 # Esto varia si son facturas B por lotes, que creo que no hacemos.
        cbt_hasta = cbte_nro + 1
        
        # Creo que el unico impuesto que tenemos que tener en cuenta es IVA.
        imp_trib = "0.00"         # importe total otros conceptos
        imp_tot_conc = "0.00"     # importe total conceptos no gravado
        imp_op_ex = "0.00"        # importe total operaciones exentas
        moneda_id = 'PES'         # actualmente no se permite otra monedaWSFEv1
        moneda_ctz = '1.000'

        # inicializar la estructura de factura (interna)
        self.wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
            cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
            imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
            fecha_serv_desde, fecha_serv_hasta,
            moneda_id, moneda_ctz)

        # 4: 10.5%, 5: 21%, 6: 27% (no enviar si es otra alicuota)
        if comprobante_cedir.gravado.id == 2:
            id = 5
            base_imp = imp_neto      # neto gravado por esta alicuota
            importe = imp_iva       # importe de iva liquidado por esta alicuota
            self.wsfev1.AgregarIva(id, base_imp, importe)
        elif comprobante_cedir.gravado.id == 3:
            id = 4
            base_imp = imp_neto      # neto gravado por esta alicuota
            importe = imp_iva       # importe de iva liquidado por esta alicuota
            self.wsfev1.AgregarIva(id, base_imp, importe)

        # llamar al webservice de AFIP para autorizar la factura y obtener CAE:
        self.wsfev1.CAESolicitar()

        # Si es nota de credito o debito necesito
        # wsfev1.AgregarCmpAsoc


        # datos devueltos por AFIP:
        return {
            "resultado": self.wsfev1.Resultado,
            "reproceso": self.wsfev1.Reproceso,
            "cae": self.wsfev1.CAE,
            "vencimiento": self.wsfev1.Vencimiento,
            "mensaje_error_afip": self.wsfev1.ErrMsg,
            "mensaje_obs_afip": self.wsfev1.Obs,
            "numero": cbte_nro
        }
    
    def consultar_cae(self, comprobante_cedir, cbte_nro):
        # De nuevo, el numero tendria que ser el del comprobante, pero limitaciones.
        return WSFEv1.CompConsultar(comprobante_cedir.codigo_afip, comprobante_cedir.nro_terminal, cbte_nro)


if __name__ == "__main__":
    privada = sys.argv[1]
    certificado = sys.argv[2]
    cuit = sys.argv[3]
    f = Facturador(privada, certificado, cuit)
    comprobante_cedir = Comprobante.objects.get(id=18658)
    comprobante_afip = f.emitir_en_afip(comprobante_cedir)
    print(comprobante_afip)
    print(f.consultar_cae(comprobante_cedir, comprobante_afip["numero"]))