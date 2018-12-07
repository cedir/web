from datetime import datetime
from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito


class CreateInformeFactoryTest(TestCase):
    def setUp(self):
        self.tipo_comprobante_liquidacion = TipoComprobante.objects.create(nombre='Liquidacion')
        self.tipo_comprobante_factura = TipoComprobante.objects.create(nombre='Factura')

    def test_factory_success(self):
        comprobante = Comprobante.objects.create(tipo_comprobante=self.tipo_comprobante_liquidacion,
                                                 numero=1,
                                                 nombre_cliente='',
                                                 domicilio_cliente='',
                                                 nro_cuit='',
                                                 gravado_paciente='',
                                                 condicion_fiscal='',
                                                 responsable='',
                                                 sub_tipo='A',
                                                 estado=Comprobante.NO_COBRADO,
                                                 total_cobrado=0,
                                                 fecha_emision=datetime.today(),
                                                 fecha_recepcion=datetime.today()
                                                 )
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created, CalculadorInformeFactura))

        comprobante = Comprobante.objects.create(tipo_comprobante=self.tipo_comprobante_factura,
                                                 numero=2,
                                                 nombre_cliente='',
                                                 domicilio_cliente='',
                                                 nro_cuit='',
                                                 gravado_paciente='',
                                                 condicion_fiscal='',
                                                 responsable='',
                                                 sub_tipo='A',
                                                 estado=Comprobante.NO_COBRADO,
                                                 total_cobrado=0,
                                                 fecha_emision=datetime.today(),
                                                 fecha_recepcion=datetime.today()
                                                 )
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created, CalculadorInformeNotaCredito))

