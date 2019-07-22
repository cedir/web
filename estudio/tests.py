from datetime import datetime
import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION
from rest_framework import status

from estudio.models import Estudio


class CrearEstudioTest(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
        self.estudio_data = {'fecha': datetime.today().date(), 'paciente': 1, 'practica': 1, 'medico': 1,
                             'obra_social': 1, 'medico_solicitante': 1, 'anestesista': 1}

    def test_crear_estudio(self):
        self.assertEqual(Estudio.objects.all().count(), 0)

        response = self.client.post('/api/estudio/', self.estudio_data)

        self.assertEqual(Estudio.objects.all().count(), 1)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        content = json.loads(response.content)
        estudio = Estudio.objects.get(pk=content.get('id'))
        self.assertEquals(estudio.paciente_id, self.estudio_data.get('paciente'))
        self.assertEquals(estudio.fecha, self.estudio_data.get('fecha'))
        self.assertEquals(estudio.obra_social_id, self.estudio_data.get('obra_social'))
        self.assertEquals(estudio.medico_id, self.estudio_data.get('medico'))
        self.assertIsNotNone(estudio.public_id)
        self.assertIsNot(estudio.public_id, u'')
        self.assertEquals(len(estudio.public_id), 32)

    def test_create_estudio_returns_error_if_practica_is_empty(self):
        self.estudio_data.pop('practica')
        response = self.client.post('/api/estudio/', self.estudio_data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.content, '{"practica":["This field is required."]}')

    def test_create_estudio_sucess_crea_un_log(self):
        ct = ContentType.objects.get_for_model(Estudio)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk).count(), 0)
        response = self.client.post('/api/estudio/', self.estudio_data)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk).count(), 1)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk).first().action_flag, ADDITION)

    def test_update_estudio_no_crea_log(self):
        ct = ContentType.objects.get_for_model(Estudio)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk).count(), 0)

        estudio = Estudio.objects.create(fecha=datetime.today().date(), paciente_id=1, practica_id=1, medico_id=1,
                                         obra_social_id=1, medico_solicitante_id=1, anestesista_id=1)

        self.estudio_data['fecha'] = '2019-03-07'
        response = self.client.put('/api/estudio/{}/'.format(estudio.id), data=json.dumps(self.estudio_data), content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk).count(), 0)
