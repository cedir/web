from datetime import datetime
from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito, CalculadorInformeNotaDebito


class CreateInformeFactoryTest(TestCase):
    def setUp(self):
        self.tipo_comprobante_factura = TipoComprobante.objects.create(nombre='Factura')
        self.tipo_comprobante_nota_debito = TipoComprobante.objects.create(nombre='Nota De Debito')
        self.tipo_comprobante_nota_credito = TipoComprobante.objects.create(nombre='Nota De Credito')

    def test_factory_success(self):
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
        self.assertTrue(isinstance(instance_created, CalculadorInformeFactura))

        comprobante = Comprobante.objects.create(tipo_comprobante=self.tipo_comprobante_nota_debito,
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
        self.assertTrue(isinstance(instance_created, CalculadorInformeNotaDebito))

        comprobante = Comprobante.objects.create(tipo_comprobante=self.tipo_comprobante_nota_credito,
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

