# -*- coding: utf-8 -*-
from decimal import Decimal

from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito, CalculadorInformeNotaDebito


class CreateInformeFactoryTest(TestCase):
    """
    Estos tests se aseguran de que el factory cree el calculador correcto para
    cada tipo de comprobante.
    """
    def setUp(self):
        self.tipo_comprobante_factura = TipoComprobante.objects.create(
            nombre='Factura')
        self.tipo_comprobante_nota_debito = TipoComprobante.objects.create(
            nombre='Nota De Debito')
        self.tipo_comprobante_nota_credito = TipoComprobante.objects.create(
            nombre='Nota De Credito')

    def test_factory_factura(self):
        comprobante = Comprobante(
            tipo_comprobante=self.tipo_comprobante_factura)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created, CalculadorInformeFactura))

    def test_factory_nota_debito(self):
        comprobante = Comprobante(
            tipo_comprobante=self.tipo_comprobante_nota_debito)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created,
                                   CalculadorInformeNotaDebito))

    def test_factory_nota_credito(self):
        comprobante = Comprobante(
            tipo_comprobante=self.tipo_comprobante_nota_credito)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created,
                                   CalculadorInformeNotaCredito))


class TestCaluloRetencionImpositiva(TestCase):
    """
    Estos tests checkean la logica de la retencion impositiva,
    que cambia segun si la presentacion va por AMR o no.
    """
    fixtures = ["comprobantes.json", "practicas.json", "anestesistas.json",
                "presentaciones.json", "obras_sociales.json", "estudios.json", "medicos.json", "pacientes.json"]

    def test_retencion_impositiva_es_cero_si_no_hay_presentacion(self):
        comprobante = Comprobante.objects.get(pk=3)
        self.assertIsNone(comprobante.presentacion.first())
        calculador = calculador_informe_factory(comprobante)
        self.assertEquals(calculador.retencion_cedir, Decimal("0.00"))

    def test_retencion_impositiva_presentacion_cobrada(self):
        """
        Comprobante de presentación con pago.
        """
        comprobante = Comprobante.objects.get(pk=2)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        pago = presentacion.pago.first()
        self.assertIsNotNone(pago)
        retencion_esperada = pago.gasto_administrativo * \
            presentacion.total_facturado / Decimal(100)
        calculador = calculador_informe_factory(comprobante)
        self.assertEquals(calculador.retencion_impositiva, retencion_esperada)

    def test_retencion_impositiva_para_presentacion_no_cobrada_que_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=1)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        self.assertIsNone(presentacion.pago.first())
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal(
            "32.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_impositiva, retencion_esperada)

    def test_retencion_impositiva_para_presentacion_no_cobrada_que_no_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=4)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        self.assertIsNone(presentacion.pago.first())
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal(
            "25.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_impositiva, retencion_esperada)