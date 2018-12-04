from django.test import TestCase
from .models import Comprobante, TipoComprobante
from .calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformePresentacion


class CreateInformeFactoryTest(TestCase):
    def setUp(self):
        self.tipo_comprobante_liquidacion = TipoComprobante.objects.create(nombre='Liquidacion')
        self.tipo_comprobante_factura = TipoComprobante.objects.create(nombre='Factura')

    def test_factory_success(self):
        comprobante = Comprobante.objects.create(tipo=self.tipo_comprobante_liquidacion)
        instance_created = calculador_informe_factory(comprobante)
        assert isinstance(instance_created, CalculadorInformeFactura)

        comprobante = Comprobante.objects.create(tipo=self.tipo_comprobante_factura)
        instance_created = calculador_informe_factory(comprobante)
        assert isinstance(instance_created, CalculadorInformePresentacion)
