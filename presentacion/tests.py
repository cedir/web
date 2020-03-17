import json
from decimal import Decimal
from mock import patch

from django.test import TestCase, Client
from django.contrib.auth.models import User

from presentacion.models import Presentacion
from obra_social.models import ObraSocial
from estudio.models import Estudio
from comprobante.models import Comprobante, ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO
from comprobante.afip import AfipError

class TestDetallesObrasSociales(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_detalle_osde(self):
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.fecha_cobro = None
        presentacion.save()
        response = self.client.get('/api/presentacion/1/get_detalle_osde/')
        assert response.content != ''

    def test_detalle_amr(self):
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.fecha_cobro = None
        presentacion.save()
        response = self.client.get('/api/presentacion/1/get_detalle_amr/')
        assert response.content != ''

class TestEstudiosDePresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_get_estudios_de_presentacion(self):
        presentacion = Presentacion.objects.get(pk=1)
        n_estudios = len(presentacion.estudios.all())
        assert n_estudios != 0
        response = self.client.get('/api/presentacion/1/estudios/')
        estudios_response = json.loads(response.content)
        assert len(estudios_response) == n_estudios

class TestCrearPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_crear_presentacion_ok(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 9,
                }
            ]
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 201
        presentacion = Presentacion.objects.get(pk=json.loads(response.content)['id'])
        assert presentacion.estado == Presentacion.ABIERTO
        assert presentacion.comprobante is None

    def test_crear_presentacion_actualiza_estudios(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        assert estudio.importe_estudio == Decimal("10000.00")
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 9,
                }
            ]
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        estudio = Estudio.objects.get(pk=9)
        assert estudio.presentacion_id != 0

class TestAbrirPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    @patch('comprobante.comprobante_asociado.Afip')
    def test_abrir_presentacion_ok(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10

        presentacion = Presentacion.objects.get(pk=1)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_FACTURA
        assert presentacion.comprobante.estado == Comprobante.NO_COBRADO
        response = self.client.patch('/api/presentacion/1/abrir/')
        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.ABIERTO
        assert Comprobante.objects.get(pk=pk_comprobante_viejo).estado == Comprobante.ANULADO
        assert presentacion.comprobante == None

    @patch('comprobante.comprobante_asociado.Afip')
    def test_abrir_presentacion_no_pendiente_falla(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        response = self.client.patch('/api/presentacion/1/abrir/')
        assert response.status_code == 400
        assert presentacion.estado == Presentacion.ABIERTO

        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.COBRADO
        presentacion.save()
        response = self.client.patch('/api/presentacion/1/abrir/')
        assert response.status_code == 400
        assert presentacion.estado == Presentacion.COBRADO
        assert not afip.emitir_comprobante.called

class TestCerrarPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    @patch('comprobante.serializers.Afip')
    def test_cerrar_presentacion_ok(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "nro_terminal": 99,
            "sub_tipo": "A",
            "responsable": "Cedir",
            "gravado_id": 1,
            "periodo": "Mayo 1968"
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante is not None

    @patch('comprobante.serializers.Afip')
    def test_cerrar_presentacion_cerrada_con_liquidacion(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.return_value = None
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 2,
            "periodo": "Mayo 1968"
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante is not None
        assert not afip.emitir_comprobante.called

    @patch('comprobante.serializers.Afip')
    def cerrar_presentacion_no_abierta_da_400(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.side_effect = AfipError
        comprobantes_antes = Comprobante.objects.all().count()
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.PENDIENTE
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "nro_terminal": 99,
            "sub_tipo": "A",
            "responsable": "Cedir",
            "gravado_id": 1,
            "periodo": "Mayo 1968"
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')
        comprobantes_despues = Comprobante.objects.all().count()
        assert response.status_code == 400
        assert comprobantes_antes == comprobantes_despues

    @patch('comprobante.serializers.Afip')
    def test_error_de_afip_no_guarda_comprobante_en_db(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.side_effect = AfipError
        comprobantes_antes = Comprobante.objects.all().count()
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "nro_terminal": 99,
            "sub_tipo": "A",
            "numero": 40,
            "responsable": "Cedir",
            "gravado_id": 1,
            "periodo": "Mayo 1968"
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')
        comprobantes_despues = Comprobante.objects.all().count()
        assert response.status_code == 500
        assert comprobantes_antes == comprobantes_despues