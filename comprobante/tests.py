from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal

from .models import LineaDeComprobante
from .serializers import CrearComprobanteAFIPSerializer, CrearLineaDeComprobanteSerializer

class TestPostComprobantes(TestCase):
    fixtures = ['comprobantes.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.cliente = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')
        self.linea_data = {
            'concepto': 'hola',
            'porcentaje_iva': '10.5',
            'importe_neto': '500'
        }


    def test_crear_linea_serializer_crea_objeto_linea(self):
        linea_serializer = CrearLineaDeComprobanteSerializer(data=self.linea_data)
        
        assert isinstance(linea_serializer, CrearLineaDeComprobanteSerializer)
        assert linea_serializer.is_valid()
        
        linea_db = linea_serializer.save()
        
        assert isinstance(linea_db, LineaDeComprobante)
        assert linea_db.concepto == self.linea_data['concepto']
        assert linea_db.importe_neto == Decimal(self.linea_data['importe_neto'])

    def test_crear_linea_serializer_calcula_correctamente_iva(self):
        linea_serializer = CrearLineaDeComprobanteSerializer(data=self.linea_data)
        
        assert linea_serializer.is_valid()
        
        linea = linea_serializer.save()
        importe_neto = Decimal(self.linea_data['importe_neto'])
        porcentaje_iva = Decimal(self.linea_data['porcentaje_iva'])
        
        assert linea.iva == importe_neto * porcentaje_iva / Decimal(100)

    def test_crear_linea_serializer_calcula_correctamente_total(self):
        linea_serializer = CrearLineaDeComprobanteSerializer(data=self.linea_data)
        
        assert linea_serializer.is_valid()
        
        linea = linea_serializer.save()
        importe_neto = Decimal(self.linea_data['importe_neto'])
        porcentaje_iva = Decimal(self.linea_data['porcentaje_iva'])
        
        total = importe_neto + importe_neto * porcentaje_iva / Decimal(100)
        
        assert linea.sub_total == total
