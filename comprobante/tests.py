# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
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


class TestCaluloRetencionCedir(TestCase):
    fixtures = ["comprobantes.json", "presentaciones.json", "obras_sociales.json"]
    def test_retencion_cedir_es_cero_si_no_hay_presentacion(self):
        comprobante = Comprobante.objects.get(pk=3)
        calculador = calculador_informe_factory(comprobante)
        self.assertEquals(calculador.retencion_cedir, 0)

    def test_retencion_cedir_presentacion_cobrada(self):
        """
        Comprobante de presentación con pago.
        """
        comprobante = Comprobante.objects.get(pk=2)
        presentacion = comprobante.presentacion.all().first()
        pago = presentacion.pago.get()
        retencion_esperada = pago.gasto_administrativo * presentacion.total_facturado / Decimal(100)
        calculador = calculador_informe_factory(comprobante)
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)

    def test_retencion_cedir_para_presentacion_no_cobrada_que_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=1)
        presentacion = comprobante.presentacion.all().first()
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal("32.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)

    def test_retencion_cedir_para_presentacion_no_cobrada_que_no_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=4)
        presentacion = comprobante.presentacion.all().first()
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal("25.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)
