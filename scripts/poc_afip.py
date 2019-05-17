#!/usr/bin/python
# -*- coding: utf8 -*-

# importar modulos python
import datetime

# importar componentes del módulo PyAfipWs
from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1

from comprobante.models import Comprobante, LineaDeComprobante

# inicializar la estructura de factura (interna)
wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
    cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
    imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
    fecha_serv_desde, fecha_serv_hasta, #--
    moneda_id, moneda_ctz)


# agregar subtotales por tasa de iva (repetir por cada alicuota):
id = 5              # 4: 10.5%, 5: 21%, 6: 27% (no enviar si es otra alicuota)
base_imp = 100      # neto gravado por esta alicuota
importe = 21        # importe de iva liquidado por esta alicuota
wsfev1.AgregarIva(id, base_imp, importe)

# agregar otros impuestos (repetir por cada tributo diferente)
id = 99                              # tipo de tributo (ver tabla)
desc = 'Impuesto Municipal Matanza'  # descripción del tributo
base_imp = 100                       # base imponible
alic = 1                             # alicuota iva
importe = 1                          # importe liquidado del tributo
wsfev1.AgregarTributo(id, desc, base_imp, alic, importe)

# llamar al webservice de AFIP para autorizar la factura y obtener CAE:
wsfev1.CAESolicitar()

# datos devueltos por AFIP:
print "Resultado", wsfev1.Resultado
print "Reproceso", wsfev1.Reproceso
print "CAE", wsfev1.CAE
print "Vencimiento", wsfev1.Vencimiento
print "Mensaje Error AFIP", wsfev1.ErrMsg
print "Mensaje Obs AFIP", wsfev1.Obs

# guardar mensajes xml (para depuración)
open("xmlrequest.xml","wb").write(wsfev1.XmlRequest)
open("xmlresponse.xml","wb").write(wsfev1.XmlResponse)

# ejemplo de obtención de atributos xml específicos
wsfev1.AnalizarXml("XmlResponse")
print wsfev1.ObtenerTagXml('CAE')
print wsfev1.ObtenerTagXml('Concepto')
print wsfev1.ObtenerTagXml('Obs',0,'Code')
print wsfev1.ObtenerTagXml('Obs',0,'Msg')


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
        cacert = None   # "afip_ca_info.crt" para verificar canal seguro

        # conectar

        ok = wsfev
rapper, cacert)
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
        self.wsfev1.SetTicketAcceso(ta)
        self.wsfev1.Cuit = cuit

    def emitir_factura(self, factura_cedir):
        lineas = LineaDeComprobante.objects.filter(comprobante = factura_cedir.id)
        # datos de la factura de prueba (encabezado):
        tipo_cbte = factura_cedir.codigo_afip
        punto_vta = factura_cedir.nro_terminal
        cbte_nro = factura_cedir.numero
        fecha = factura_cedir.fecha_emision
        concepto = 2
        tipo_doc = factura.tipo_id_afip() 
        nro_doc = factura.numero_id_afip()
        cbt_desde = factura_cedir.numero
        cbt_hasta = factura_cedir.numero
        imp_total = factura_cedir.total_facturado      # sumatoria total
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
        moneda_id = 'PES'         # actualmente no se permite otra moneda
        moneda_ctz = '1.000'

        # inicializar la estructura de factura (interna)
        wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
            cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
            imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
            fecha_serv_desde, fecha_serv_hasta, #--
            moneda_id, moneda_ctz)

    def emiitr_nota_credito(self, nota_credito_cedir):
        # ...
        return cae
        
    def emiitr_nota_debito(self, nota_debito_cedir):
        # ...
        return cae
        
    def consultar_afip(self, cae):
        return comprobante_afip


if __name__ == "__main__":
    # Buscar ids copadas
    factura_a_cedir = Comprobante.get()
    factura_b_cedir = Comprobante.get()
    nota_de_credito_a_cedir = Comprobante.get()
    nota_de_debito_a_cedir = Comprobante.get()
    nota_de_credito_b_cedir = Comprobante.get()
    nota_de_debito_b_cedir = Comprobante.get()

    print("Factura A:")
    print(consultar_afip(emitir_factura(factura_a_cedir)))
    print(consultar_afip(emitir_factura(factura_b_cedir)))
    print(consultar_afip(emitir_factura(nota_de_credito_a_cedir)))
    print(consultar_afip(emitir_factura(nota_de_debito_a_cedir)))
    print(consultar_afip(emitir_factura(nota_de_credito_b_cedir)))
    print(consultar_afip(emitir_factura(nota_de_debito_b_cedir)))