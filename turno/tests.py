from django.test import TestCase
from django.test import Client
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser, User
from views import anunciar
from estudio.models import Estudio
from turno.models import Turno



class TurnosTest(TestCase):
    fixtures = ['turnos.json']

    def setUp(self):
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='12345')

        self.user = User.objects.create(username="walter")
        self.request = HttpRequest()
        self.request.user = self.user

    def test_anunciar_truno(self):
        """
        Deberia crear un estudio por cada practica del turno
        """

        self.assertEqual(Estudio.objects.all().count(), 0)
        turno = Turno.objects.get(pk=1)
        
        #response = self.client.post('turno/1/anunciar/', {})  # TODO: esto es ideal en vez de llamar anunciar, pero no esta andando.
        #print response
        
        response = anunciar(self.request, turno.id)
        self.assertContains(response, '{"status": true, "message": "Success"}')

        self.assertEqual(Estudio.objects.all().count(), turno.practicas.all().count())

