from datetime import datetime
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import AnonymousUser, User
from views import anunciar
from estudio.models import Estudio
from turno.models import Turno, PeriodoSinAtencion


class TurnosTest(TestCase):
    fixtures = ['fixtures/turnos.json', 'fixtures/pacientes.json', 'fixtures/medicos.json',
                'fixtures/practicas.json', 'fixtures/obras_sociales.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
        self.turno_data = {'hora_inicio': '12:00', 'hora_fin_estimada': '13:00',
                           'fecha_turno': datetime.today().date(), 'id-sala': 1, 'id-paciente': 1, 'id-medico': 1,
                           'id-obra-social': 1, 'observacion_turno': 'test'}

    def test_anunciar_truno(self):
        """
        Deberia crear un estudio por cada practica del turno.
        """
        self.assertEqual(Estudio.objects.all().count(), 0)
        turno = Turno.objects.get(pk=1)
        
        response = self.client.post('/turno/1/anunciar/', {})
        self.assertContains(response, '{"status": true, "message": "Success"}')

        self.assertEqual(Estudio.objects.all().count(), turno.practicas.all().count())

    def test_guardar_truno_success(self):
        self.assertEqual(Turno.objects.all().count(), 1)
        response = self.client.get('/turno/guardar/', self.turno_data)
        self.assertContains(response, '{"status": 1, "message": "El turno se ha creado correctamente."}')
        self.assertEqual(Turno.objects.all().count(), 2)

    def test_guardar_truno_error_superposicion_de_turnos(self):
        self.assertEqual(Turno.objects.all().count(), 1)
        turno_existente = Turno.objects.get(pk=1)
        turno_existente.fechaTurno = datetime.today().date()
        turno_existente.horaInicio = '12:00'
        turno_existente.hora_fin_estimada = '12:30'
        turno_existente.save()

        data = self.turno_data
        data['hora_inicio'] = turno_existente.horaInicio
        data['hora_fin_estimada'] = turno_existente.hora_fin_estimada
        data['fecha_turno'] = turno_existente.fechaTurno

        response = self.client.get('/turno/guardar/', data)
        self.assertContains(
            response,
            '{"status": 0, "message": "Error, se ha detectado superposici\u00f3n de turnos. Por favor, haga click en Mostrar y vuelva a intentarlo."}'
        )
        self.assertEqual(Turno.objects.all().count(), 1)

    def test_guardar_truno_error_medico_de_licencia(self):
        self.assertEqual(PeriodoSinAtencion.objects.all().count(), 0)
        self.assertEqual(Turno.objects.all().count(), 1)

        PeriodoSinAtencion.objects.create(fecha_inicio=datetime.today().date(), fecha_fin=datetime.today().date(),
                                          medico_id=1)
        data = self.turno_data
        data['hora_inicio'] = '12:00'
        data['hora_fin_estimada'] = '13:00'
        data['fecha_turno'] = datetime.today().date()

        response = self.client.get('/turno/guardar/', data)

        self.assertContains(response, '{"status": 0, "message": "El medico no atiende en la fecha seleccionada"}')
        self.assertEqual(Turno.objects.all().count(), 1)

    def test_guardar_truno_error_fecha_turno_es_feriado(self):
        self.assertEqual(PeriodoSinAtencion.objects.all().count(), 0)
        self.assertEqual(Turno.objects.all().count(), 1)

        PeriodoSinAtencion.objects.create(fecha_inicio=datetime.today().date(), fecha_fin=datetime.today().date(),
                                          medico=None)
        data = self.turno_data
        data['hora_inicio'] = '12:00'
        data['hora_fin_estimada'] = '13:00'
        data['fecha_turno'] = datetime.today().date()

        response = self.client.get('/turno/guardar/', data)

        self.assertContains(response, '{"status": 0, "message": "El medico no atiende en la fecha seleccionada"}')
        self.assertEqual(Turno.objects.all().count(), 1)
