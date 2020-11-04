from django.test import TestCase, Client
from django.contrib.auth.models import User
from .serializers import CrearComprobanteSerializer

class TestPostComprobantes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.cliente = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_serializer_crear_comprobante_crea_objeto_comprobantes(self):
        c = CrearComprobanteSerializer(data={
            'tipo_comprobante_id': '1',
            'sub_tipo': 'B',
            'responsable': 'Cedir',
            'gravado_id': '2',
            'nombre_cliente': 'Homero J. Simpson',
            'domicilio_cliente': 'Avenida Siempreviva 742',
            'nro_cuit': '20420874120',
            'condicion_fiscal': 'CONSUMIDOR FINAL',
            'lineas': [
                { 'concepto': 'Esta es una linea', 'importeNeto': '500'},
                { 'concepto': 'Esta es una linea', 'importeNeto': '511.11'}
            ],
            'neto': 0,
        })
        if c.is_valid():
            print('Era valido')
        c = c.save()
        print(c)