from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework import status
from mock import patch
from datetime import date
from comprobante.comprobante_asociado import crear_comprobante_asociado, TipoComprobanteAsociadoNoValidoException
from comprobante.afip import AfipErrorRed, AfipErrorValidacion
from comprobante.models import Comprobante, TipoComprobante, LineaDeComprobante, \
    ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA

NUMERO_TERMINAL = 91

class TestComprobantesAsociados(TestCase):

    fixtures = ['comprobantes.json']

    def setUp(self):
        self.user = User.objects.create_user(username='usuario', password='xxxxxx1', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='usuario', password='xxxxxx1')
        
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
        with self.assertRaises(TipoComprobanteAsociadoNoValidoException):
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
        with self.assertRaises(TipoComprobanteAsociadoNoValidoException):
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
        with self.assertRaises(TipoComprobanteAsociadoNoValidoException):
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
        with self.assertRaises(TipoComprobanteAsociadoNoValidoException):
            crear_comprobante_asociado(1, 500, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA)

    def test_crear_comprobante_asociado_falla_si_el_comprobante_no_existe(self):
        with self.assertRaises(Comprobante.DoesNotExist):
            crear_comprobante_asociado(50, 100, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    @patch('comprobante.comprobante_asociado.Afip')
    def test_crear_comprobante_asociado_falla_si_no_se_realiza_la_conexion_con_afip(self, afip_mock):
        afip_mock.side_effect = AfipErrorRed

        with self.assertRaises(AfipErrorRed):
            crear_comprobante_asociado(1, 100, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    @patch('comprobante.comprobante_asociado.Afip')
    def test_crear_comprobante_asociado_falla_si_afip_no_valida_el_comprobante(self, afip_mock):
        afip = afip_mock()

        afip.emitir_comprobante.side_effect = AfipErrorValidacion

        with self.assertRaises(AfipErrorValidacion):
            crear_comprobante_asociado(1, 100, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

    @patch('comprobante.comprobante_asociado.Afip')
    def test_comprobante_no_se_guarda_en_bd_si_afip_devuelve_error(self, afip_mock):
        afip = afip_mock()

        afip.emitir_comprobante.side_effect = AfipErrorValidacion
        
        cantidad_inicial = Comprobante.objects.count()

        with self.assertRaises(AfipErrorValidacion):
            crear_comprobante_asociado(1,199,ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        
        assert cantidad_inicial == Comprobante.objects.count()
        
        afip.emitir_comprobante.side_effect = AfipErrorRed

        with self.assertRaises(AfipErrorRed):
            crear_comprobante_asociado(1, 100, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)

        assert cantidad_inicial == Comprobante.objects.count()

    @patch('comprobante.comprobante_asociado.Afip')
    def test_cliente_obtiene_el_json_del_comprobante_cuando_genera_un_comprobante_asociado(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 14
        response = self.client.post('/api/comprobante/crear_comprobante_asociado/', {'id-comprobante-asociado': 1, 'importe': 200, 'id-tipo': ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO})

        comp = response.data['data']

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(comp['numero'], 14)
        self.assertEquals(comp['tipo_comprobante']['nombre'], (TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)).nombre)
        self.assertEquals(comp['tipo_comprobante']['id'], ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        self.assertEquals(comp['total_facturado'], '200.00')