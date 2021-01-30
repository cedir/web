from django.test import TestCase, Client
from django.contrib.auth.models import User

from anestesista.models import Anestesista
from estudio.models import Estudio, ID_SUCURSAL_CEDIR, ID_SUCURSAL_HOSPITAL_ITALIANO

class TestAnestesistas(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_pago_anestesista_filtra_por_sucursal(self):
        assert estudios.count() > 0
        response = self.client.get(f'/api/anestesista/1/pago/2013/11/?sucursal={ID_SUCURSAL_CEDIR}')
        print(response.content)
        estudios = Estudio.objects.filter(anestesista__id=1, sucursal=ID_SUCURSAL_HOSPITAL_ITALIANO)
        assert estudios.count() > 0