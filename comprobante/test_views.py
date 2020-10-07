from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework import status
from mock import patch
from comprobante.models import TipoComprobante, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO

class TestViews(TestCase):

    fixtures = ['comprobantes.json']

    def setUp(self):
        self.user = User.objects.create_user(username='usuario', password='xxxxxx1', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='usuario', password='xxxxxx1')

    @patch('comprobante.comprobante_asociado.Afip')
    def test_cliente_obtiene_el_json_del_comprobante_cuando_genera_un_comprobante_asociado(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 14
        response = self.client.post('/api/comprobante/crear_comprobante_asociado', {'id-comprobante-asociado': 1, 'importe': 200, 'concepto': ''})

        comp = response.data['data']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(comp['numero'], 14)
        self.assertEqual(comp['tipo_comprobante']['nombre'], (TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)).nombre)
        self.assertEqual(comp['tipo_comprobante']['id'], ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        self.assertEqual(comp['total_facturado'], '200.00')

        response = self.client.post('/api/comprobante/crear_comprobante_asociado', {'id-comprobante-asociado': 1, 'importe': 200, 'concepto': 'ajustes'})

        comp = response.data['data']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(comp['numero'], 14)
        self.assertEqual(comp['tipo_comprobante']['nombre'], (TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)).nombre)
        self.assertEqual(comp['tipo_comprobante']['id'], ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        self.assertEqual(comp['total_facturado'], '200.00')

    def test_informe_ventas_ok(self):

        response = self.client.get("/comprobante/informe/ventas/cedir/2019/09/?responsable=cedir&anio=2019&mes=09")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], 'application/x-zip-compressed')
