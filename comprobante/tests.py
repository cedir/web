from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal

from .models import LineaDeComprobante, Gravado
from .serializers import CrearComprobanteAFIPSerializer, CrearLineaDeComprobanteSerializer

class TestCrearLineaSerializer(TestCase):
    fixtures = ['comprobantes.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.cliente = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')
        self.linea_data = {
            'concepto': 'hola',
            'gravado_id': '2',
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
        porcentaje_iva = Gravado.objects.get(pk=self.linea_data['gravado_id'])
        
        assert linea.iva == importe_neto * porcentaje_iva / Decimal(100)

    def test_crear_linea_serializer_calcula_correctamente_total(self):
        linea_serializer = CrearLineaDeComprobanteSerializer(data=self.linea_data)
        
        assert linea_serializer.is_valid()
        
        linea = linea_serializer.save()
        importe_neto = Decimal(self.linea_data['importe_neto'])
        porcentaje_iva = Gravado.objects.get(pk=self.linea_data['gravado_id'])
        
        total = importe_neto + importe_neto * porcentaje_iva / Decimal(100)
        
        assert linea.sub_total == total

    def test_crear_linea_serializer_no_valido_si_id_iva_no_existe(self):
        self.linea_data['gravado_id'] = Gravado.objects.count() + 1
        linea_serializer = CrearLineaDeComprobanteSerializer(data=self.linea_data)

        assert not linea_serializer.is_valid()
        assert 'gravado_id' in linea_serializer.errors

class TestCrearLineaSerializer(TestCase):
    fixtures = ['comprobantes.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.cliente = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')
        self.comprobante_data = {
            'tipo_comprobante_id': 1,
            'sub_tipo': 'B',
            'responsable': 'Cedir',
            'gravado_id': '1',
            'neto': 100,
            'nombre_cliente': 'Homero',
            'domicilio_cliente': 'Avenida Siempreviva 123',
            'nro_cuit': '20420874120',
            'condicion_fiscal': 'RESPONSABLE INSCRIPTO',
            'concepto': 'Este es un concepto',
            'lineas': [
                {
                    'concepto': 'Esta es la primera linea',
                    'importe_neto': 50
                },
                {
                    'concepto': 'Esta es la segunda linea',
                    'importe_neto': 60
                }
            ],
        }
    
    def test_comprobante_afip_serializer_funciona_si_no_envian_lineas(self):
        del self.comprobante_data['lineas']
        comprobante_serializer = CrearComprobanteAFIPSerializer(data=self.comprobante_data)

        assert comprobante_serializer.is_valid()
        comprobante = comprobante_serializer.save()

        neto = self.comprobante_data['neto']

        iva = Gravado.objects.get(pk=self.comprobante_data['gravado_id']).porcentaje * neto

        total = neto + neto * iva / Decimal(100)

        assert comprobante.total_facturado == total
        assert comprobante.tipo_comprobante.id == self.comprobante_data['tipo_comprobante_id']
        assert comprobante.sub_tipo == self.comprobante_data['sub_tipo']
        assert comprobante.nombre_cliente == self.comprobante_data['nombre_cliente']

        linea = LineaDeComprobante.objects.get(comprobante=comprobante)

        assert linea.importe_neto == neto
        assert linea.sub_total == total
        assert linea.concepto == self.comprobante_data['concepto']
        
