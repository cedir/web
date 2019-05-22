#!/usr/bin/python
# -*- coding: utf8 -*-

# importar modulos python
import datetime

# importar componentes del módulo PyAfipWs
from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1

import wsgi
from comprobante.models import Comprobante, LineaDeComprobante

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
        tipo_cbte = comprobante_cedir.codigo_afip
        punto_vta = comprobante_cedir.nro_terminal
        cbte_nro = long(self.wsfev1.CompUltimoAutorizado(tipo_cbte, punto_vta) or 0)
        # fecha = comprobante_cedir.fecha_emision.strftime("%Y%m%d")
        fecha = datetime.datetime.now().strftime("%Y%m%d")
        concepto = 2
        tipo_doc = comprobante_cedir.tipo_id_afip
        nro_doc = comprobante_cedir.nro_id_afip
        cbt_desde = cbte_nro + 1
        cbt_hasta = cbte_nro + 1
        imp_total = comprobante_cedir.total_facturado      # sumatoria total
        imp_tot_conc = "0.00"     # importe total conceptos no gravado
        imp_neto = sum([l.importe_neto for l in lineas])       # importe neto gravado (todas las alicuotas)
        imp_iva = sum([l.iva for l in lineas])        # importe total iva liquidado (idem)
        imp_trib = "0.00"         # importe total otros conceptos
        imp_op_ex = "0.00"        # importe total operaciones exentas
        fecha_cbte = fecha
        fecha_venc_pago = fecha
        # Fechas del período del servicio facturado (solo si concepto != 1)
        fecha_serv_desde = fecha
        fecha_serv_hasta = fecha
        moneda_id = 'PES'         # actualmente no se permite otra monedaWSFEv1
        moneda_ctz = '1.000'

        # inicializar la estructura de factura (interna)
        self.wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
            cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
            imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
            fecha_serv_desde, fecha_serv_hasta,
            moneda_id, moneda_ctz)

        # dudas aca
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
        print "Resultado", self.wsfev1.Resultado
        print "Reproceso", self.wsfev1.Reproceso
        print "CAE", self.wsfev1.CAE
        print "Vencimiento", self.wsfev1.Vencimiento
        print "Mensaje Error AFIP", self.wsfev1.ErrMsg
        print "Mensaje Obs AFIP", self.wsfev1.Obs
    
    def consultar_afip(self, cae):
        return comprobante_afip


if __name__ == "__main__":

    f = Facturador("privada.csr", "test.crt", 20389047938)


    # Buscar ids copadas
    comprobante_cedir = Comprobante.objects.get(id=18658)
    f.emitir_en_afip(comprobante_cedir)