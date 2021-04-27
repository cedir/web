# -*- coding: utf-8 -*-
from datetime import datetime
from httplib2 import ServerNotFoundError
from mock import patch

from django.test import TestCase
from comprobante.models import Comprobante, TipoComprobante, Gravado, LineaDeComprobante, \
    ID_DOCUMENTO_AFIP_TIPO_CUIT, ID_DOCUMENTO_AFIP_TIPO_CUIL, ID_DOCUMENTO_AFIP_TIPO_DNI
from comprobante.afip import Afip, AfipErrorValidacion, AfipErrorRed


TICKET = "ticket"


class TestAfipAPI(TestCase):
    '''
    Test sobre la clase AFIP.
    '''
    fixtures = ["comprobantes.json"]

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_sobre_singleton_afip_devuelve_la_misma_instancia_luego_de_crearse_mas_de_una_vez(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsfev1.return_value.Conectar.return_value = True
        instancia1 = Afip()
        instancia2 = Afip()

        assert instancia1 is instancia2

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
            afip.emitir_comprobante(comprobante, [])

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
            afip.emitir_comprobante(comprobante, [])

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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)
        afip.emitir_comprobante(comprobante, [])
        assert comprobante.cae == 1
        assert comprobante.vencimiento_cae.strftime("%Y-%m-%d") == "3019-12-31"
        assert comprobante.numero == 1

    @patch("comprobante.afip._Afip.autenticar")
    @patch("comprobante.afip.WSAA", autospec=True)
    @patch("comprobante.afip.WSFEv1")
    def test_ticket_expirado_renueva_y_emite(self, mock_wsfev1, mock_wsaa, mock_afip):
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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)
        assert mock_afip.call_count == 2
        afip.emitir_comprobante(comprobante, [])
        assert mock_afip.call_count == 3
        mock_wsfev1.return_value.CAESolicitar.assert_called()

    @patch("comprobante.afip._Afip.autenticar")
    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_ticket_valido_no_renueva_y_emite(self, mock_wsfev1, mock_wsaa, mock_afip):
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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)
        assert mock_afip.call_count == 2
        afip.emitir_comprobante(comprobante, [])
        assert mock_afip.call_count == 2
        mock_wsfev1.return_value.CAESolicitar.assert_called()

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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.gravado = Gravado.objects.get(pk=1)
        afip.emitir_comprobante(comprobante, [])
        assert comprobante.cae == 1
        assert comprobante.vencimiento_cae.strftime("%Y-%m-%d") == "3019-12-31"
        assert comprobante.numero == 1

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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.gravado = Gravado.objects.get(pk=2)
        afip.emitir_comprobante(comprobante, [])
        assert comprobante.cae == 1
        assert comprobante.vencimiento_cae.strftime("%Y-%m-%d") == "3019-12-31"
        assert comprobante.numero == 1

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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.gravado = Gravado.objects.get(pk=3)
        afip.emitir_comprobante(comprobante, [])
        assert comprobante.cae == 1
        assert comprobante.vencimiento_cae.strftime("%Y-%m-%d") == "3019-12-31"
        assert comprobante.numero == 1

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
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        comprobante = Comprobante.objects.get(pk=1)

        comprobante.tipo_comprobante = TipoComprobante.objects.get(pk=3)
        comprobante.factura = Comprobante.objects.get(pk=2)
        afip.emitir_comprobante(comprobante, [])
        assert comprobante.cae == 1
        assert comprobante.vencimiento_cae.strftime("%Y-%m-%d") == "3019-12-31"
        assert comprobante.numero == 1

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_emitir_factura(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=1), "A")
        factura = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Cedir",
            "sub_tipo": "A",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 91,
            "total_facturado": "2800.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=1),
        })
        # Creamos una linea de comprobante, parte necesaria de un comprobante para nuestro sistema.
        lineas_factura = [LineaDeComprobante(**{
            "comprobante": factura,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]
        afip.emitir_comprobante(factura, lineas_factura)
        assert factura.cae == 1

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_emitir_nota_de_debito(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=1), "A")
        factura = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Cedir",
            "sub_tipo": "A",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 91,
            "total_facturado": "2800.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=1),
        })
        lineas_factura = [LineaDeComprobante(**{
            "comprobante": factura,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]
        numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=3), "A")
        nota_debito = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Cedir",
            "sub_tipo": "A",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 91,
            "total_facturado": "2800.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=3),
            "factura": factura
        })
        lineas_nota_debito = [LineaDeComprobante(**{
            "comprobante": nota_debito,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]
        afip.emitir_comprobante(nota_debito, lineas_nota_debito)
        assert nota_debito.cae == 1

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_emitir_nota_de_credito(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "30191231"
        afip = Afip()
        numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=1), "A")
        factura = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Cedir",
            "sub_tipo": "A",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 91,
            "total_facturado": "2800.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=1),
        })
        lineas_factura = [LineaDeComprobante(**{
            "comprobante": factura,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]
        numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=3), "A")
        nota_debito = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Cedir",
            "sub_tipo": "A",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 91,
            "total_facturado": "2800.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=3),
            "factura": factura
        })
        lineas_nota_debito = [LineaDeComprobante(**{
            "comprobante": nota_debito,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]
        numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=4), "A")
        nota_credito = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Cedir",
            "sub_tipo": "A",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 91,
            "total_facturado": "2800.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=4),
            "factura": nota_debito  # Ponemos como comprobante asociado la factura que hicimos recien.
        })
        lineas_nota_credito = [LineaDeComprobante(**{
            "comprobante": nota_credito,
            "importe_neto": 2800.00,
            "sub_total": 2800.00,
            "iva": 0,
        })]
        afip.emitir_comprobante(nota_credito, lineas_nota_credito)
        assert nota_credito.cae == 1

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_emitir_factura_de_credito_electronica(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=5), "B")
        factura_electronica = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Brunetti",
            "sub_tipo": "B",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 3,
            "total_facturado": "100000.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=5),
        })
        lineas_factura_electronica = [LineaDeComprobante(**{
            "comprobante": factura_electronica,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]
        afip.emitir_comprobante(factura_electronica, lineas_factura_electronica)
        assert factura_electronica.cae == 1

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_emitir_nota_de_debito_electronica(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=5), "B")
        factura_electronica = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Brunetti",
            "sub_tipo": "B",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 3,
            "total_facturado": "100000.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=5),
        })
        lineas_factura_electronica = [LineaDeComprobante(**{
            "comprobante": factura_electronica,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]
        numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=6), "B")
        Comprobante.objects.filter(nro_terminal=3, tipo_comprobante=TipoComprobante.objects.get(pk=6), numero=numero).delete()
        nota_de_debito_electronica = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Brunetti",
            "sub_tipo": "B",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 3,
            "total_facturado": "100000.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=6),
            "factura": factura_electronica
        })
        lineas_nota_de_debito_electronica = [LineaDeComprobante(**{
            "comprobante": nota_de_debito_electronica,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]
        afip.emitir_comprobante(nota_de_debito_electronica, lineas_nota_de_debito_electronica)
        assert nota_de_debito_electronica.cae == 1

    @patch("comprobante.afip.WSAA")
    @patch("comprobante.afip.WSFEv1")
    def test_emitir_nota_de_credito_electronica(self, mock_wsfev1, mock_wsaa):
        mock_wsaa.return_value.Autenticar.return_value = TICKET
        mock_wsaa.return_value.Expirado.return_value = False
        mock_wsfev1.return_value.Conectar.return_value = True
        mock_wsfev1.return_value.CompUltimoAutorizado.return_value = 0
        mock_wsfev1.return_value.AgregarIva.return_value = None
        mock_wsfev1.return_value.CAESolicitar.return_value = None

        mock_wsfev1.return_value.Resultado = "A"
        mock_wsfev1.return_value.CAE = 1
        mock_wsfev1.return_value.Vencimiento = "30191231"

        afip = Afip()
        numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=5), "B")
        factura_electronica = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Brunetti",
            "sub_tipo": "B",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 3,
            "total_facturado": "100000.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=5),
        })
        lineas_factura_electronica = [LineaDeComprobante(**{
            "comprobante": factura_electronica,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]
        numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=6), "B")
        Comprobante.objects.filter(nro_terminal=3, tipo_comprobante=TipoComprobante.objects.get(pk=6), numero=numero).delete()
        nota_de_debito_electronica = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Brunetti",
            "sub_tipo": "B",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 3,
            "total_facturado": "100000.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=6),
            "factura": factura_electronica
        })
        lineas_nota_de_debito_electronica = [LineaDeComprobante(**{
            "comprobante": nota_de_debito_electronica,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]
        numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=7), "B")
        nota_de_credito_electronica = Comprobante(**{
            "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
            "domicilio_cliente": " - Springfield - (CP:2000)",
            "nro_cuit": "30604958640",
            "gravado_paciente": "",
            "condicion_fiscal": "EXENTO",
            "gravado": Gravado.objects.get(pk=1),
            "responsable": "Brunetti",
            "sub_tipo": "B",
            "estado": "PENDIENTE",
            "numero": numero,
            "nro_terminal": 3,
            "total_facturado": "100000.00",
            "total_cobrado": "0.00",
            "fecha_emision": datetime.today(),
            "fecha_recepcion": datetime.today(),
            "tipo_comprobante": TipoComprobante.objects.get(pk=7),
            "factura": nota_de_debito_electronica
        })
        lineas_nota_de_credito_electronica = [LineaDeComprobante(**{
            "comprobante": nota_de_credito_electronica,
            "importe_neto": 100000.00,
            "sub_total": 100000.00,
            "iva": 0,
        })]
        afip.emitir_comprobante(nota_de_credito_electronica, lineas_nota_de_credito_electronica)
        assert nota_de_credito_electronica.cae == 1

class TestTipoIdAfip(TestCase):
    fixtures = ["comprobantes.json"]

    def test_dni(self):
        comprobante = Comprobante.objects.get(pk=1)
        comprobante.nro_cuit = "38905723"
        comprobante.save()
        comprobante = Comprobante.objects.get(pk=1)
        assert comprobante.tipo_id_afip == ID_DOCUMENTO_AFIP_TIPO_DNI

    def test_cuit(self):
        comprobante = Comprobante.objects.get(pk=1)
        comprobante.nro_cuit = "30-38905723-7"
        comprobante.save()
        comprobante = Comprobante.objects.get(pk=1)
        assert comprobante.tipo_id_afip == ID_DOCUMENTO_AFIP_TIPO_CUIT

