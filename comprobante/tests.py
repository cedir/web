# -*- coding: utf-8 -*-
from decimal import Decimal
from httplib2 import ServerNotFoundError
from mock import patch

from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante, Gravado
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito, CalculadorInformeNotaDebito
from comprobante.afip import Afip, AfipErrorValidacion, AfipErrorRed


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
            linea.total_cobrado
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


TICKET = "ticket"


class TestAfipAPI(TestCase):
    '''
    Test sobre la clase AFIP.
    '''
    fixtures = ["comprobantes.json"]

    @patch("comprobante.afip.WSFEv1")
    def test_error_de_conexion_en_constructor_lanza_excepcion(self, mock_wsfev1):
        mock_wsfev1.return_value.Conectar.side_effect = ServerNotFoundError
        with self.assertRaises(AfipErrorRed):
            Afip("", "", 1)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_error_de_conexion_lanza_excepcion(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.side_effect = ServerNotFoundError

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)
        with self.assertRaises(AfipErrorRed):
            afip.emitir_comprobante(comprobante)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_comprobante_rechazado_por_webservice_lanza_excepcion(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "R"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)
        with self.assertRaises(AfipErrorValidacion):
            afip.emitir_comprobante(comprobante)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_comprobante_aceptado_por_weservice_setea_cae(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(comprobante.cae, 1)
        self.assertEquals(comprobante.vencimiento_cae, "3019-12-31")
        self.assertEquals(comprobante.numero, 1)

    @patch("comprobante.afip.WSAA", autospec=True)
    @patch("comprobante.afip.WSFEv1")
    def test_ticket_expirado_renueva_y_emite(self, mock_wsfev1, mock_wsaa):
        '''
        Se mockea WSAA.Expirado para que devuelva false en la primer llamada y luego true,
        de manera de testear que en ese escenario, emitir_comprobante llama a WSAA.Autenticar
        antes de cumplir su tarea (en total se llama dos veces con al del constructor).
        '''
        mock_wsaa.return_value.Autenticar.side_effect = [TICKET, TICKET]
        mock_wsaa.return_value.Expirado.side_effect = [True, False]
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 2)
        mock_wsfev1.return_value.CAESolicitar.assert_is_called()

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_ticket_valido_no_renueva_y_emite(self, mock_wsfev1, mock_wsaa):
        '''
        Se mockea WSAA.Expirado para que devuelva true y se testea que WSAA.Autenticar sea
        llamada una sola vez, para asegurarnos de que no se pierde tiempo piediendo
        tickets inutilmente. 
        '''
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 1)
        mock_wsfev1.return_value.CAESolicitar.assert_is_called()

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_comprobante_con_gravado_excento(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.gravado = Gravado.objects.get(pk=1)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(comprobante.cae, 1)
        self.assertEquals(comprobante.vencimiento_cae, "3019-12-31")
        self.assertEquals(comprobante.numero, 1)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_comprobante_con_gravado_10_5(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.gravado = Gravado.objects.get(pk=2)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(comprobante.cae, 1)
        self.assertEquals(comprobante.vencimiento_cae, "3019-12-31")
        self.assertEquals(comprobante.numero, 1)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_comprobante_con_gravado_21(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.gravado = Gravado.objects.get(pk=3)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(comprobante.cae, 1)
        self.assertEquals(comprobante.vencimiento_cae, "3019-12-31")
        self.assertEquals(comprobante.numero, 1)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_comprobante_con_comprobantes_asociados(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "3019-12-31"

        afip = Afip("", "", 1)
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.tipo_comprobante = TipoComprobante.objects.get(pk=3)
        comprobante.factura = Comprobante.objects.get(pk=2)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(comprobante.cae, 1)
        self.assertEquals(comprobante.vencimiento_cae, "3019-12-31")
        self.assertEquals(comprobante.numero, 1)
        