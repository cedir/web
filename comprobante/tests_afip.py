# -*- coding: utf-8 -*-
from httplib2 import ServerNotFoundError
from mock import patch

from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante, Gravado
from comprobante.afip import Afip, AfipErrorValidacion, AfipErrorRed


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
            Afip()

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_error_de_conexion_lanza_excepcion(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.side_effect = ServerNotFoundError

        afip = Afip()
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

        afip = Afip()
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

        afip = Afip()
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

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 2)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 3)
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

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 2)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(mock_wsaa.return_value.Autenticar.call_count, 2)
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

        afip = Afip()
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

        afip = Afip()
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

        afip = Afip()
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

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.tipo_comprobante = TipoComprobante.objects.get(pk=3)
        comprobante.factura = Comprobante.objects.get(pk=2)
        afip.emitir_comprobante(comprobante)
        self.assertEquals(comprobante.cae, 1)
        self.assertEquals(comprobante.vencimiento_cae, "3019-12-31")
        self.assertEquals(comprobante.numero, 1)
        