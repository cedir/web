# -*- coding: utf-8 -*-
from decimal import Decimal
import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from comprobante.models import Comprobante, TipoComprobante
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito


class TestHerramientaInformeComprobantesContadora(TestCase):
    """
    Estos para la herramienta que genera el informe de comprobantes.
    """
    fixtures = ["comprobantes.json", "practicas.json", "anestesistas.json",
                "presentaciones.json", "obras_sociales.json", "estudios.json", "medicos.json", "pacientes.json"]
    def setUp(self):
        self.lineas_informe = [calculador_informe_factory(c) for c in Comprobante.objects.all()]

    def test_informe_propiedades_definidas(self):
        for linea in self.lineas_informe:
            linea.total_facturado
            linea.neto
            linea.iva
            linea.honorarios_anestesia
            linea.retencion_anestesia
            linea.retencion_impositiva
            linea.retencion_cedir
            linea.sala_recuperacion
            linea.total_medicamentos
            linea.total_material_especifico
            linea.honorarios_medicos
            linea.uso_de_materiales
            linea.honorarios_solicitantes


class CreateInformeFactoryTest(TestCase):
    """
    Estos tests se aseguran de que el factory cree el calculador correcto para
    cada tipo de comprobante.
    """
    fixtures = ["comprobantes.json"]

    def setUp(self):
        self.tipo_comprobante_factura = TipoComprobante.objects.get(pk=1)
        self.tipo_comprobante_liquidacion = TipoComprobante.objects.get(pk=2)
        self.tipo_comprobante_nota_debito = TipoComprobante.objects.get(pk=3)
        self.tipo_comprobante_nota_credito = TipoComprobante.objects.get(pk=4)
        self.tipo_comprobante_factura_electronica = TipoComprobante.objects.get(pk=5)
        self.tipo_comprobante_nota_debito_electronica = TipoComprobante.objects.get(pk=6)
        self.tipo_comprobante_nota_credito_electronica = TipoComprobante.objects.get(pk=7)

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
                                   CalculadorInformeFactura))

    def test_factory_nota_credito(self):
        comprobante = Comprobante(
            tipo_comprobante=self.tipo_comprobante_nota_credito)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created,
                                   CalculadorInformeNotaCredito))

    def test_factory_factura_de_credito_electronica(self):
        comprobante = Comprobante(
            tipo_comprobante=self.tipo_comprobante_factura)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created, CalculadorInformeFactura))

    def test_factory_nota_debito_electronica(self):
        comprobante = Comprobante(
            tipo_comprobante=self.tipo_comprobante_nota_debito)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created,
                                   CalculadorInformeFactura))

    def test_factory_nota_credito_electronica(self):
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

class TestEndpoint(TestCase):
    fixtures = ["comprobantes.json", "practicas.json", "anestesistas.json",
                "presentaciones.json", "obras_sociales.json", "estudios.json", "medicos.json", "pacientes.json"]

    def test_endpoint_informe_comprobantes(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')
        response = self.client.get('/api/comprobantes/', {
            "mes": 7,
            "anio": 2012,
        })
        content = json.loads(response.content)
        linea_informe = content[0]
        self.assertIsInstance(linea_informe, dict)
