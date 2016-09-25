from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import AnonymousUser, User
from views import anunciar
from estudio.models import Estudio
from turno.models import Turno


class TurnosTest(TestCase):
    fixtures = ['turnos.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')

    def test_anunciar_truno(self):
        """
        Deberia crear un estudio por cada practica del turno.
        TODO: para que este test corra hay que poner que el estudio se cree con idFacturacion = 1.
        Los fixtures fallan porque no permite crear una presentacion con id = 0 y fallan los fereign keys.
        """

        self.assertEqual(Estudio.objects.all().count(), 0)
        turno = Turno.objects.get(pk=1)
        
        response = self.client.post('/turno/1/anunciar/', {})
        self.assertContains(response, '{"status": true, "message": "Success"}')

        self.assertEqual(Estudio.objects.all().count(), turno.practicas.all().count())

