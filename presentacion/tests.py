from datetime import datetime
import json
from decimal import Decimal
from mock import patch

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION, CHANGE
from rest_framework import status

from estudio.models import Estudio
from presentacion.models import Presentacion

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

    def test_get_estudios_de_presentacion_abierta(self):
        presentacion = Presentacion.objects.get(pk=1)
        n_estudios = len(presentacion.estudios.all())
        assert n_estudios != 0
        response = self.client.get('/api/presentacion/1/estudios/')
        estudios_response = json.loads(response.content)
        assert len(estudios_response) == n_estudios

    def test_get_estudios_de_presentacion_cerrada(self):
        presentacion = Presentacion.objects.get(pk=1)
        n_estudios = len(presentacion.estudios.all())
        assert n_estudios != 0
        response = self.client.get('/api/presentacion/1/estudios/')
        estudios_response = json.loads(response.content)
        assert len(estudios_response) == n_estudios