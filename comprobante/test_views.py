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
        response = self.client.post('/api/comprobante/crear_comprobante_asociado', {'id-comprobante-asociado': 1, 'importe': 200, 'id-tipo': ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO})

        comp = response.data['data']

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(comp['numero'], 14)
        self.assertEquals(comp['tipo_comprobante']['nombre'], (TipoComprobante.objects.get(pk = ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)).nombre)
        self.assertEquals(comp['tipo_comprobante']['id'], ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO)
        self.assertEquals(comp['total_facturado'], '200.00')