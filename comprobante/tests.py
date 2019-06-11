# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from mock import patch, Mock
from comprobante.models import Comprobante, TipoComprobante
from comprobante.calculador_informe import calculador_informe_factory, CalculadorInformeFactura, CalculadorInformeNotaCredito, CalculadorInformeNotaDebito
from comprobante.afip import Afip, AfipErrorValidacion, AfipErrorRed
from httplib2 import ServerNotFoundError

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
        retencion_esperada = pago.gasto_administrativo * presentacion.total_facturado / Decimal(100)
        calculador = calculador_informe_factory(comprobante)
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)

    def test_retencion_cedir_para_presentacion_no_cobrada_que_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=1)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        self.assertIsNone(presentacion.pago.first())
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal("32.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)

    def test_retencion_cedir_para_presentacion_no_cobrada_que_no_va_por_AMR(self):
        comprobante = Comprobante.objects.get(pk=4)
        presentacion = comprobante.presentacion.first()
        self.assertIsNotNone(presentacion)
        self.assertIsNone(presentacion.pago.first())
        calculador = calculador_informe_factory(comprobante)
        retencion_esperada = Decimal("25.00") * presentacion.total_facturado / Decimal("100.00")
        self.assertEquals(calculador.retencion_cedir, retencion_esperada)


TICKET = "ticket"

class TestAfipAPI(TestCase):
    '''
    Test sobre la clase AFIP.
    '''

    @patch("comprobante.afip.WSMTXCA")
    def test_error_de_conexion_en_constructor_lanza_excepcion(self, mock_wsmtxca):
        mock_wsmtxca.return_value.Conectar.side_effect = ServerNotFoundError
        with self.assertRaises(AfipErrorRed):
            Afip("", "", 1)

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSMTXCA")
    def test_error_de_conexion_lanza_excepcion(self, mock_wsmtxca, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsmtxca.return_value.Conectar.return_value = True
        mock_wsmtxca.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsmtxca.return_value.AgregarIva.return_value = None
        mock_wsmtxca.return_value.CAESolicitar.side_effect = ServerNotFoundError
        
        afip = Afip("", "", 1)
        with self.assertRaises(AfipErrorRed):
            afip.emitir_comprobante([], {}, [], tipo_cbte=1, punto_vta=1)


    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSMTXCA")
    def test_comprobante_rechazado_por_webservice_lanza_excepcion(self, mock_wsmtxca, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsmtxca.return_value.Conectar.return_value = True
        mock_wsmtxca.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsmtxca.return_value.AgregarIva.return_value = None
        mock_wsmtxca.return_value.CAESolicitar.return_value = None

        mock_wsmtxca.return_value.Resultado = "R"
        
        afip = Afip("", "", 1)
        with self.assertRaises(AfipErrorValidacion):
            afip.emitir_comprobante([], {}, [], tipo_cbte=1, punto_vta=1)
    
    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSMTXCA")
    def test_comprobante_aceptado_por_weservice_devuelve_dict(self, mock_wsmtxca, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsmtxca.return_value.Conectar.return_value = True
        mock_wsmtxca.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsmtxca.return_value.AgregarIva.return_value = None
        mock_wsmtxca.return_value.CAESolicitar.return_value = None

        mock_wsmtxca.return_value.Resultado = "A"

        afip = Afip("", "", 1)
        self.assertTrue(isinstance(afip.emitir_comprobante([], {}, [], tipo_cbte=1, punto_vta=1), dict))
            

    @patch("comprobante.afip.WSAA", autospec=True)
    @patch("comprobante.afip.WSMTXCA")
    def test_ticket_expirado_renueva_y_emite(self, mock_wsmtxca, mock_wsaa):
        mock_wsaa.return_value.Expirado.side_effect = [True, False]
        mock_wsaa.return_value.Autenticar.side_effect = [TICKET, TICKET]
        mock_wsmtxca.return_value.Conectar.return_value = True
        mock_wsmtxca.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsmtxca.return_value.AgregarIva.return_value = None
        mock_wsmtxca.return_value.CAESolicitar.return_value = None

        mock_wsmtxca.return_value.Resultado = "A"

        afip = Afip("", "", 1)
        afip.emitir_comprobante([], {}, [], tipo_cbte=1, punto_vta=1)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 2)
        mock_wsmtxca.return_value.CAESolicitar.assert_is_called()


    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSMTXCA")
    def test_ticket_valido_no_renueva_y_emite(self, mock_wsmtxca, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsmtxca.return_value.Conectar.return_value = True
        mock_wsmtxca.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsmtxca.return_value.AgregarIva.return_value = None
        mock_wsmtxca.return_value.CAESolicitar.return_value = None

        mock_wsmtxca.return_value.Resultado = "A"

        afip = Afip("", "", 1)
        afip.emitir_comprobante([], {}, [], tipo_cbte=1, punto_vta=1)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 1)
        mock_wsmtxca.return_value.CAESolicitar.assert_is_called()