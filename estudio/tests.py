from datetime import datetime
import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from estudio.models import Estudio


class CrearEstudioTest(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')

    def test_crear_truno(self):
        self.assertEqual(Estudio.objects.all().count(), 0)

        estudio_data = {'fecha': datetime.today().date(), 'paciente': 1, 'practica': 1, 'medico': 1,
                        'obra_social': 1, 'medico_solicitante': 1, 'anestesista': 1}
        response = self.client.post('/api/estudio/', estudio_data)

        self.assertEqual(Estudio.objects.all().count(), 1)
        self.assertEquals(response.status_code, 201)

        content = json.loads(response.content)
        estudio = Estudio.objects.get(pk=content.get('id'))
        self.assertEquals(estudio.paciente_id, estudio_data.get('paciente'))
        self.assertEquals(estudio.fecha, estudio_data.get('fecha'))
        self.assertEquals(estudio.obra_social_id, estudio_data.get('obra_social'))
        self.assertEquals(estudio.medico_id, estudio_data.get('medico'))

        self.assertIsNotNone(estudio.public_id)
        self.assertIsNot(estudio.public_id, u'')

    def test_create_estudio_returns_error_if_practica_is_empty(self):
        pass