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
from pyafipws.wsmtx import WSMTXCA
from xml.parsers.expat import ExpatError



class Facturador(object):
    def __init__(self, privada, certificado, cuit):
        # instanciar el componente para factura electrónica mercado interno
        self.afip = WSMTXCA()
        self.afip.LanzarExcepciones = True
        
        # datos de conexión (cambiar URL para producción)
        cache = None
        wsdl = "https://fwshomo.afip.gov.ar/wsmtxca/services/MTXCAService?wsdl"
        proxy = ""
        wrapper = ""    # "pycurl" para usar proxy avanzado / propietarios
        # datos de la factura de prueba (encabezado):
        cacert = None   # "afip_ca_info.crt" para verificar canal seguro

        # conectar
        try:
            ok = self.afip.Conectar(cache, wsdl, proxy, wrapper, cacert)
        except ExpatError:
            RuntimeError("Error: parece que el servicio de la AFIP esta caido.")
        if not ok:
            raise RuntimeError("Error afip: %s" % WSAA.Excepcion)


        # autenticarse frente a AFIP (obtención de ticket de acceso):
        cert = certificado       # archivos a tramitar previamente ante AFIP 
        clave = privada     # (ver manual)
        wsaa_url = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
        self.ta = WSAA().Autenticar("wsmtxca", cert, clave, wsaa_url, debug=True)
        if not self.ta:
            raise RuntimeError("Error WSAA: %s" % WSAA.Excepcion)

        # establecer credenciales (token y sign) y cuit emisor:
        self.afip.SetTicketAcceso(self.ta)
        self.afip.Cuit = cuit

    def emitir_en_afip(self, comprobante_cedir):
        lineas = LineaDeComprobante.objects.filter(comprobante = comprobante_cedir.id)

        
        # Habria que usar la fecha del comprobante, pero la API me limita a facturar cerca de la fecha actual.
        # fecha = comprobante_cedir.fecha_emision.strftime("%Y%m%d")
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
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
        if comprobante_cedir.gravado.id == 1:
            imp_neto = "0.00"
            imp_op_ex = sum([l.importe_neto for l in lineas])
            imp_subtotal = sum([l.sub_total for l in lineas])
        else:
            imp_neto = sum([l.importe_neto for l in lineas])       # importe neto gravado (todas las alicuotas)
            imp_op_ex = "0.00"        # importe total operaciones exentas
            imp_subtotal = imp_neto

        imp_iva = sum([l.iva for l in lineas])        # importe total iva liquidado (idem)
        concepto = 2 # Servicios, lo unico que hace el CEDIR.

        # En realidad habria que usar el numero del comprobante, pero con este certificado no puedo.
        cbte_nro = long(self.afip.CompUltimoAutorizado(tipo_cbte, punto_vta) or 0)
        cbt_desde = cbte_nro + 1 # Esto varia si son facturas B por lotes, que creo que no hacemos.
        cbt_hasta = cbte_nro + 1
        
        # Creo que el unico impuesto que tenemos que tener en cuenta es IVA.
        imp_trib = "0.00"         # importe total otros conceptos
        imp_tot_conc = "0.00"     # importe total conceptos no gravado
        moneda_id = 'PES'         # actualmente no se permite otra monedaafip
        moneda_ctz = '1.000'

        # inicializar la estructura de factura (interna)
        # Por algun motivo que no entiendo, nuestro subtotal no le gusta y quiere que el mande el neto como subtotal. Sino, no lo emite.
        self.afip.CrearFactura(concepto=concepto, tipo_doc=tipo_doc, nro_doc=nro_doc, tipo_cbte=tipo_cbte, punto_vta=punto_vta,
            cbt_desde=cbt_desde, cbt_hasta=cbt_hasta, imp_total=imp_total, imp_tot_conc=imp_tot_conc, imp_neto=imp_neto,
            imp_subtotal=imp_subtotal, imp_trib=imp_trib, imp_op_ex=imp_op_ex, fecha_cbte=fecha_cbte, fecha_venc_pago=fecha_venc_pago, 
            fecha_serv_desde=fecha_serv_desde, fecha_serv_hasta=fecha_serv_hasta, #--
            moneda_id=moneda_id, moneda_ctz=moneda_ctz, observaciones=None, caea=None, fch_venc_cae=None)

        # Si es una nota de debito (3) o credito (4), agregamos el comprobante asociado
        if comprobante_cedir.tipo_comprobante in [3, 4]:
            comprobante_asociado = Comprobantes.objects.get(id=factura)
            tipo = comrpobante_asociado.codigo_afip
            punto_vta = comprobante_asociado.nro_terminal
            nro = comprobante_asociado.numero # Curiosamente, la afip no se queja si este numero es invalido.
            self.afip.AgregarCmpAsoc(tipo, pto_vta, nro)


        # No se si ya tenemos algun metodo que haga esta traduccion
        # 4: 10.5%, 5: 21%, 6: 27% (no enviar si es otra alicuota)
        if comprobante_cedir.gravado.id == 2:
            id_iva = 4
            base_imp = imp_neto      # neto gravado por esta alicuota
            importe = imp_iva       # importe de iva liquidado por esta alicuota
            self.afip.AgregarIva(id_iva, base_imp, importe)
        elif comprobante_cedir.gravado.id == 3:
            id_iva = 5
            base_imp = imp_neto      # neto gravado por esta alicuota
            importe = imp_iva       # importe de iva liquidado por esta alicuota
            self.afip.AgregarIva(id_iva, base_imp, importe)
        else:
            id_iva = 2

        for linea in lineas:
            u_mtx = 123456
            cod_mtx = "1234567890"
            codigo = "P0001"
            ds = linea.concepto
            qty = "1.0000"
            umed = 7
            precio = str(linea.importe_neto)
            bonif = "0.00"
            cod_iva = id_iva
            imp_iva = str(linea.iva)
            imp_subtotal = linea.sub_total
            ok = self.afip.AgregarItem(u_mtx, cod_mtx, codigo, ds, qty,
                        umed, precio, bonif, cod_iva, imp_iva, imp_subtotal)

        # llamar al webservice de AFIP para autorizar la factura y obtener CAE:
        self.afip.CAESolicitar()

        # datos devueltos por AFIP:
        return {
            "resultado": self.afip.Resultado,
            "reproceso": self.afip.Reproceso,
            "cae": self.afip.CAE,
            "vencimiento": self.afip.Vencimiento,
            "mensaje_error_afip": self.afip.ErrMsg,
            "mensaje_obs_afip": self.afip.Obs,
            "numero": cbte_nro + 1
        }
    
    def consultar_cae(self, comprobante_cedir, cbte_nro):
        self.afip.ConsultarComprobante(comprobante_cedir.codigo_afip, comprobante_cedir.nro_terminal, cbte_nro)
        return {
            "fecha": self.afip.FechaCbte,
            "numero": self.afip.CbteNro,
            "punto_venta": self.afip.PuntoVenta,
            "vencimiento": self.afip.Vencimiento,
            "importe_total": self.afip.ImpTotal,
            "CAE": self.afip.CAE,
            "emision_tipo": self.afip.EmisionTipo
        }


if __name__ == "__main__":
    privada = sys.argv[1]
    certificado = sys.argv[2]
    cuit = sys.argv[3]
    
    f = Facturador(privada, certificado, cuit)
    for id_comprobante in range(18500, 18650):
        print(id_comprobante)
        comprobante_cedir = Comprobante.objects.get(id=id_comprobante)
        # Nos salteamos las liquidaciones
        if comprobante_cedir.tipo_comprobante.id == 2:
            continue
        comprobante_afip = f.emitir_en_afip(comprobante_cedir)
        print(comprobante_afip)
        print(f.consultar_cae(comprobante_cedir, comprobante_afip["numero"]))