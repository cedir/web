from django.test import TestCase, Client
from django.contrib.auth.models import User
from paciente.models import Paciente
import json

class TestFormularioPaciente(TestCase):
    fixtures = ['pacientes.json']
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')
        self.paciente_prueba = {
            'nombre': 'Test',
            'apellido': 'Pacientes',
            'dni': 12312313,
            'domicilio': 'Calle Falsa 123',
            'telefono': '123456789',
            'sexo': 'Femenino',
            'fechaNacimiento': '01/01/1976',
            'nro_afiliado': '12345',
            'email': 'lalala123@gmail.com',
        }

    def test_crear_paciente_falla_si_dni_existe_en_db(self):
        paciente_db = Paciente.objects.get(pk=1)
        paciente = self.paciente_prueba
        paciente['dni'] = paciente_db.dni

        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)

        assert response['status'] == 0

        paciente['dni'] = 12312313

        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)

        assert response['status'] == 1

    def test_crear_paciente_falla_si_nro_afiliado_no_es_alfanumerico(self):
        paciente = self.paciente_prueba
        paciente['nro_afiliado'] = '12345.'

        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)
        assert response['status'] == 0

        paciente['nro_afiliado'] = '12345 ab,cd'
        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)
        assert response['status'] == 0

        paciente['nro_afiliado'] = '12345 abcd!'
        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)
        assert response['status'] == 0

        paciente['nro_afiliado'] = '12345 abcd'
        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)
        assert response['status'] == 1

    def test_crear_paciente_guarda_paciente_en_db(self):
        cantidad_inicial = Paciente.objects.count()
        response = json.loads(self.client.post('/paciente/nuevo/', self.paciente_prueba).content)

        assert response['status'] == 1
        assert Paciente.objects.count() == cantidad_inicial + 1

    def test_crear_paciente_no_guarda_paciente_en_db_si_falla(self):
        cantidad_inicial = Paciente.objects.count()
        self.paciente_prueba['nro_afiliado'] = '12345!'
        response = json.loads(self.client.post('/paciente/nuevo/', self.paciente_prueba).content)

        assert response['status'] == 0
        assert Paciente.objects.count() == cantidad_inicial

    def test_update_paciente_falla_si_dni_existe_en_db(self):
        paciente_db = Paciente.objects.get(pk=1)
        paciente = self.paciente_prueba
        paciente['dni'] = paciente_db.dni

        response = json.loads(self.client.post('/paciente/2/actualizar/', paciente).content)

        assert response['status'] == 0

        paciente['dni'] = 12312313

        response = json.loads(self.client.post('/paciente/2/actualizar/', paciente).content)

        assert response['status'] == 1

    def test_update_paciente_falla_si_nro_afiliado_no_es_alfanumerico(self):
        paciente = self.paciente_prueba
        paciente['nro_afiliado'] = '12345.'

        response = json.loads(self.client.post('/paciente/1/actualizar/', paciente).content)
        assert response['status'] == 0

        paciente['nro_afiliado'] = '12345 ab,cd'
        response = json.loads(self.client.post('/paciente/1/actualizar/', paciente).content)
        assert response['status'] == 0

        paciente['nro_afiliado'] = '12345 abcd!'
        response = json.loads(self.client.post('/paciente/1/actualizar/', paciente).content)
        assert response['status'] == 0

        paciente['nro_afiliado'] = '12345 abcd'
        response = json.loads(self.client.post('/paciente/1/actualizar/', paciente).content)
        assert response['status'] == 1
    
    def test_update_actualiza_paciente_en_db(self):
        paciente = self.paciente_prueba

        response = json.loads(self.client.post('/paciente/nuevo/', paciente).content)
        assert response['status'] == 1

        paciente['nro_afiliado'] = '12345'
        paciente['nombre'] = 'Jorge'
        paciente['dni'] = 5248624

        id_paciente = response['idPaciente']

        response = json.loads(self.client.post('/paciente/{}/actualizar/'.format(id_paciente), paciente).content)

        paciente_act = Paciente.objects.get(pk=id_paciente)

        assert paciente_act.nroAfiliado == '12345'
        assert paciente_act.nombre == 'Jorge'
        assert paciente_act.dni == 5248624
