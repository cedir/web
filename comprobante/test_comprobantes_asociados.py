from django.test import TestCase
from datetime import datetime
from comprobante.comprobante_asociado import crear_comprobante_asociado
from comprobante.afip import Afip
from comprobante.models import Comprobante, TipoComprobante, LineaDeComprobante, \
    ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA

HTTP_BAD_REQUEST = 400
HTTP_OK = 200
NUMERO_TERMINAL = 91

class TestComprobantesAsociados(TestCase):

    fixtures = ['comprobantes.json']

    def test_crear_nota_de_credito_asociada_a_factura_valido(self):
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    def test_falla_crear_nota_de_credito_asociada_a_factura_electronica(self):
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'
        comp.total_facturado = '100000.00'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)


        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    def test_crear_nota_de_debito_asociada_a_factura_valido(self):
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)

    def test_falla_crear_nota_de_debito_asociada_a_factura_electronica(self):
        afip = Afip()
                
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.sub_tipo = 'A'
        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'
        comp.total_facturado = '100000.00'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)


        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)

    def test_crear_nota_de_credito_electronica_asociada_a_factura_electronica_valido(self):
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.sub_tipo = 'A'
        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'
        comp.total_facturado = '100000.00'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)

    def test_falla_crear_nota_de_credito_electronica_asociada_a_factura(self):
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.sub_tipo = 'A'
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)

        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)

    def test_crear_nota_de_debito_electronica_asociada_a_factura_electronica_valido(self):
        
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.sub_tipo = 'A'
        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'
        comp.total_facturado = '100000.00'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)

    def test_falla_crear_nota_de_debito_electronica_asociada_a_factura(self):
        afip = Afip()
        
        comp = Comprobante.objects.get(pk = 1)
        comp.nro_terminal = NUMERO_TERMINAL
        comp.sub_tipo = 'A'
        comp.numero = afip.consultar_proximo_numero(comp.responsable, NUMERO_TERMINAL, comp.tipo_comprobante, comp.sub_tipo)
        comp.fecha_emision = datetime.today()
        comp.fecha_recepcion = datetime.today()
        comp.nro_cuit = '30604958640'

        lineas_factura = [LineaDeComprobante(**{
            "comprobante": comp,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]

        afip.emitir_comprobante(comp,lineas_factura)
        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)
