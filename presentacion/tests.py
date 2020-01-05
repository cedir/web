import json
from decimal import Decimal
from mock import patch

from django.test import TestCase, Client
from django.contrib.auth.models import User

from presentacion.models import Presentacion
from obra_social.models import ObraSocial
from estudio.models import Estudio

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

    @patch('presentacion.serializers.Afip')
    def test_crear_presentacion_cerrada(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.return_value = None
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "estado": "Pendiente",
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
            "comprobante": {
                "tipo_id": 1,
                "nro_terminal": 99,
                "sub_tipo": "A",
                "numero": 40,
                "responsable": "Cedir",
                "gravado_id": 1
            }
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        presentacion = Presentacion.objects.get(pk=json.loads(response.content)['id'])
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante is not None

    def test_crear_presentacion_abierta(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "estado": "Abierto",
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
            "comprobante": {
                "tipo_id": 1,
                "nro_terminal": 99,
                "sub_tipo": "A",
                "numero": 40,
                "responsable": "Cedir",
                "gravado_id": 1
            }
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
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
            "estado": "Abierto",
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
            "comprobante": {
                "tipo_id": 1,
                "nro_terminal": 99,
                "sub_tipo": "A",
                "numero": 40,
                "responsable": "Cedir",
                "gravado_id": 1
            }
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        estudio = Estudio.objects.get(pk=9)
        assert estudio.presentacion_id != 0
        assert estudio.importe_estudio == Decimal(5)