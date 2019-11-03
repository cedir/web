from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante, \
    ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA

HTTP_BAD_REQUEST = 400
HTTP_OK = 200
NUMERO_TERMINAL = 91

class TestComprobantesAsociados(TestCase):

    fixtures = ['comprobantes.json']

    def test_crear_nota_de_credito_asociada_a_factura_valido(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        assert HTTP_OK == crear_comprobante_asociado(comp2, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    def test_falla_crear_nota_de_credito_asociada_a_factura_electronica(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp2.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)

        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp2, 100, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    def test_crear_nota_de_debito_asociada_a_factura_valido(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)
        assert HTTP_OK == crear_comprobante_asociado(comp2, 1200, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)

    def test_falla_crear_nota_de_debito_asociada_a_factura_electronica(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp2.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)

        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)
        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp2, 1200, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)

    def test_crear_nota_de_credito_electronica_asociada_a_factura_electronica_valido(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp2.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)
        assert HTTP_OK == crear_comprobante_asociado(comp2, 1200, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)

    def test_falla_crear_nota_de_credito_electronica_asociada_a_factura(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)
        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp2, 1200, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)

    def test_crear_nota_de_debito_electronica_asociada_a_factura_electronica_valido(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp2.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)

        assert HTTP_OK == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)
        assert HTTP_OK == crear_comprobante_asociado(comp2, 1200, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)

    def test_falla_crear_nota_de_debito_electronica_asociada_a_factura(self):
        comp = Comprobante.objects.get(pk = 1)
        comp2 = Comprobante.objects.get(pk = 2)

        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)
        assert HTTP_BAD_REQUEST == crear_comprobante_asociado(comp2, 1200, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)

    def test_obtener_comprobante_con_id_valido(self):
        
        comprobantes_list = Comprobante.objects.all()

        for i in range(1,len(comprobantes_list)):
            assert comprobantes_list[i] == obtener_comprobante_id(i)

    def test_obtener_comprobante_con_id_invalido(self):
        assert obtener_comprobante_id(232) == HTTP_BAD_REQUEST 
        assert obtener_comprobante_id(1000) == HTTP_BAD_REQUEST 
