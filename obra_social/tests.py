import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from estudio.models import Estudio

class TestDetallesObrasSociales(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json']

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_detalle_osde(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.presentacion_id == 0
        assert estudio.obra_social.pk == 1
        response = self.client.get('/api/obra_social/1/estudios_sin_presentar/')
        estudios_response = json.loads(response.content)
        assert len(estudios_response) > 0