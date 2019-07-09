# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from httplib2 import ServerNotFoundError
from mock import patch
import json

from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante, Gravado
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito, CalculadorInformeNotaDebito
from comprobante.afip import Afip, AfipErrorValidacion, AfipErrorRed


class CreateInformeFactoryTest(TestCase):
    def setUp(self):
        self.tipo_comprobante_factura = TipoComprobante.objects.create(
            nombre='Factura')
        self.tipo_comprobante_nota_debito = TipoComprobante.objects.create(
            nombre='Nota De Debito')
        self.tipo_comprobante_nota_credito = TipoComprobante.objects.create(
            nombre='Nota De Credito')

    def test_factory_factura(self):
        comprobante = Comprobante(tipo_comprobante=self.tipo_comprobante_factura)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created, CalculadorInformeFactura))

    def test_factory_nota_debito(self):
        comprobante = Comprobante(tipo_comprobante=self.tipo_comprobante_nota_debito)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created,
                                   CalculadorInformeNotaDebito))

    def test_factory_nota_credito(self):
        comprobante = Comprobante(tipo_comprobante=self.tipo_comprobante_nota_credito)
        instance_created = calculador_informe_factory(comprobante)
        self.assertTrue(isinstance(instance_created,
                                   CalculadorInformeNotaCredito))


class TestCaluloRetencionCedir(TestCase):
    fixtures = ["comprobantes.json",
                "presentaciones.json", "obras_sociales.json"]

    def test_retencion_cedir_es_cero_si_no_hay_presentacion(self):
        comprobante = Comprobante.objects.get(pk=3)
        self.assertIsNone(comprobante.presentacion.first())
        calculador = calculador_informe_factory(comprobante)
        self.assertEquals(calculador.retencion_cedir, Decimal("0.00"))

    def test_retencion_cedir_presentacion_cobrada(self):
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
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)

    def test_retencion_cedir_para_presentacion_no_cobrada_que_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=1)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        self.assertIsNone(presentacion.pago.first())
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal(
            "32.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)

    def test_retencion_cedir_para_presentacion_no_cobrada_que_no_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=4)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        self.assertIsNone(presentacion.pago.first())
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal(
            "25.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)


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


class TestCalculadorInformeComprobantes(TestCase):
    """
    Estos tests usan como fixture la facturacion completa de un mes y cargan una version serializada de un
    informe de Mariana.
    El calculador de informes tiene que producir exactamente el mismo informe que Mariana.
    Se realiza un test por cada columna del informe de Mariana, pero se suman algunos de los nuestros ya que el nuestros
    divide en mas columnas (es mas detallado).
    """
    fixtures = ["datos_para_informe_contadora.json", "pacientes.json",
                "medicos.json", "anestesistas.json", "practicas.json"]

    def setUp(self):
        with open("fixtures/informe_ejemplo.json") as informe_file:
            self.informe_ejemplo = json.loads(informe_file.read())
        self.informe_calculado = [calculador_informe_factory(
            comp) for comp in Comprobante.objects.all()]
        assert(len(self.informe_ejemplo) == len(self.informe_calculado))

        self.informe_ejemplo.sort(
            cmp=lambda x, y: int(x["numero"]) - int(y["numero"]))
        self.informe_calculado.sort(
            cmp=lambda x, y: x.comprobante.numero - y.comprobante.numero)

    def test_informe_contadora_total_facturado(self):
        for i in range(len(self.informe_calculado)):
            self.assertEquals(float(self.informe_calculado[i].total_facturado), self.informe_ejemplo[i]["total_facturado"],
                              "numero: {}, calculado: {}, ejemplo: {}".format(self.informe_ejemplo[i]["numero"], self.informe_calculado[i].total_facturado, self.informe_ejemplo[i]["total_facturado"]))

    def test_informe_contadora_iva(self):
        for i in range(len(self.informe_calculado)):
            # Lo castie a int porque en un comprobante falla por centavos, que no es problema.
            self.assertEquals(int(self.informe_calculado[i].iva), int(self.informe_ejemplo[i]["iva"]),
                              "numero: {}, calculado: {}, ejemplo: {}".format(self.informe_ejemplo[i]["numero"], self.informe_calculado[i].iva, self.informe_ejemplo[i]["iva"]))

    def test_informe_contadora_honorarios_medicos(self):
        for i in range(len(self.informe_calculado)):
            self.assertEquals(float(self.informe_calculado[i].honorarios_medicos), self.informe_ejemplo[i]["honorarios_medicos"],
                              "numero: {}, calculado: {}, ejemplo: {}".format(self.informe_ejemplo[i]["numero"], self.informe_calculado[i].honorarios_medicos, self.informe_ejemplo[i]["honorarios_medicos"]))

    def test_informe_contadora_honorarios_anestesistas(self):
        for i in range(len(self.informe_calculado)):
            self.assertEquals(float(self.informe_calculado[i].honorarios_anestesia), self.informe_ejemplo[i]["honorarios_anestesistas"],
                              "numero: {}, calculado: {}, ejemplo: {}".format(self.informe_ejemplo[i]["numero"], self.informe_calculado[i].honorarios_anestesia, self.informe_ejemplo[i]["honorarios_anestesistas"]))

    def test_informe_contadora_total_medicamentos(self):
        for i in range(len(self.informe_calculado)):
            self.assertEquals(float(self.informe_calculado[i].total_medicamentos), self.informe_ejemplo[i]["total_medicamentos"],
                              "numero: {}, calculado: {}, ejemplo: {}".format(self.informe_ejemplo[i]["numero"], self.informe_calculado[i].total_medicamentos, self.informe_ejemplo[i]["total_medicamentos"]))

    def test_informe_contadora_otros(self):
        # El informe de ejemplo que nos paso Mariana tiene esta columna agregada. Sin un informe de ejemplo mas detallados no podemos testear
        # cada uno por separado.
        for i in range(len(self.informe_calculado)):
            calculado = int(self.informe_calculado[i].retencion_impositiva + self.informe_calculado[i].retencion_cedir +
                            self.informe_calculado[i].sala_recuperacion + self.informe_calculado[i].total_material_especifico)
            ejemplo = int(self.informe_ejemplo[i]["otros"])
            self.assertEquals(calculado, ejemplo, "numero: {}, calculado: {}, ejemplo: {}".format(
                self.informe_ejemplo[i]["numero"], calculado, ejemplo))
