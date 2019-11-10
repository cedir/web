from django.test import TestCase
from mock import patch
from datetime import date
from comprobante.comprobante_asociado import crear_comprobante_asociado, TiposNoValidos
from comprobante.afip import Afip, AfipErrorRed, AfipErrorValidacion
from comprobante.models import Comprobante, TipoComprobante, LineaDeComprobante, \
    ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA

NUMERO_TERMINAL = 91

class TestComprobantesAsociados(TestCase):

    fixtures = ['comprobantes.json']

    @patch('comprobante.comprobante_asociado.Afip')
    def test_genera_comprobante_asociado_si_se_crea_una_nota_de_credito_asociada_a_factura(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10

        comp = Comprobante.objects.get(pk = 1)

        c = crear_comprobante_asociado(1, 200, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

        assert c.nombre_cliente == comp.nombre_cliente
        assert c.nro_cuit == comp.nro_cuit
        assert c.responsable == comp.responsable
        assert c.condicion_fiscal == comp.condicion_fiscal
        assert c.total_facturado == 200
        assert c.tipo_comprobante == TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        assert c.nro_terminal == comp.nro_terminal

    @patch('comprobante.comprobante_asociado.Afip')
    def test_falla_crear_comprobante_asociado_si_es_nota_de_credito_asociada_a_factura_electronica(self, mock):
        c = Comprobante.objects.get(pk = 1)
        c.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)
        c.save()
        with self.assertRaises(TiposNoValidos):
            crear_comprobante_asociado(1, 500, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    @patch('comprobante.comprobante_asociado.Afip')
    def test_genera_comprobante_asociado_si_se_crea_una_nota_de_debito_asociada_a_factura(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 11
        
        comp = Comprobante.objects.get(pk = 1)

        c = crear_comprobante_asociado(1, 300, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)

        assert c.nombre_cliente == comp.nombre_cliente
        assert c.nro_cuit == comp.nro_cuit
        assert c.responsable == comp.responsable
        assert c.condicion_fiscal == comp.condicion_fiscal
        assert c.total_facturado == 300
        assert c.tipo_comprobante == TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)
        assert c.nro_terminal == comp.nro_terminal

    @patch('comprobante.comprobante_asociado.Afip')
    def test_falla_crear_comprobante_asociado_si_es_nota_de_debito_asociada_a_factura_electronica(self, afip_mock):
        c = Comprobante.objects.get(pk = 1)
        c.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)
        c.save()
        with self.assertRaises(TiposNoValidos):
            crear_comprobante_asociado(1, 300, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO)
    
    @patch('comprobante.comprobante_asociado.Afip')
    def test_genera_comprobante_asociado_si_se_crea_una_nota_de_credito_electronica_asociada_a_factura_electronica(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 12
        
        comp = Comprobante.objects.get(pk = 1)
        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp.save()
        c = crear_comprobante_asociado(1, 400, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)

        assert c.nombre_cliente == comp.nombre_cliente
        assert c.nro_cuit == comp.nro_cuit
        assert c.responsable == comp.responsable
        assert c.condicion_fiscal == comp.condicion_fiscal
        assert c.total_facturado == 400
        assert c.tipo_comprobante == TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)
        assert c.nro_terminal == comp.nro_terminal  

    @patch('comprobante.comprobante_asociado.Afip')
    def test_falla_crear_comprobante_asociado_si_es_nota_de_credito_electronica_asociada_a_factura(self, afip_mock):
        with self.assertRaises(TiposNoValidos):
            crear_comprobante_asociado(1, 400, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA)
            
    @patch('comprobante.comprobante_asociado.Afip')
    def test_genera_comprobante_asociado_si_se_crea_una_nota_de_debito_electronica_asociada_a_factura_electronica(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 13
        
        comp = Comprobante.objects.get(pk = 1)
        comp.tipo_comprobante = TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA)
        comp.save()
        c = crear_comprobante_asociado(1, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)

        assert c.nombre_cliente == comp.nombre_cliente
        assert c.nro_cuit == comp.nro_cuit
        assert c.responsable == comp.responsable
        assert c.condicion_fiscal == comp.condicion_fiscal
        assert c.total_facturado == 500
        assert c.tipo_comprobante == TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)
        assert c.nro_terminal == comp.nro_terminal  

    @patch('comprobante.comprobante_asociado.Afip')
    def test_falla_crear_comprobante_asociado_si_es_nota_de_debito_electronica_asociada_a_factura(self, afip_mock):
        with self.assertRaises(TiposNoValidos):
            crear_comprobante_asociado(1, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)