import simplejson
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from caja.models import MovimientoCaja


class ListadoCajaTest(TestCase):
    fixtures = ['caja.json', 'medicos.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')

    def test_listado(self):
        response = self.client.get('/api/caja/', {})
        results = simplejson.loads(response.content).get('results')
        self.assertEquals(len(results), MovimientoCaja.objects.all().count())
