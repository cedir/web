from datetime import datetime, timedelta
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import AnonymousUser, User
from turno.views import anunciar, _is_feriado, _is_medico_con_licencia
from estudio.models import Estudio
from turno.models import Turno, PeriodoSinAtencion
from medico.models import Medico


class TurnosTest(TestCase):
    fixtures = ['turnos.json', 'pacientes.json', 'medicos.json',
                'practicas.json', 'obras_sociales.json']

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
        turnos_count_inicial = Turno.objects.all().count()
        response = self.client.get('/turno/guardar/', self.turno_data)
        self.assertContains(response, '{"status": 1, "message": "El turno se ha creado correctamente."}')
        self.assertEqual(Turno.objects.all().count(), turnos_count_inicial + 1)

    def test_guardar_truno_error_superposicion_de_turnos(self):
        turnos_count_inicial = Turno.objects.all().count()
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
        self.assertEqual(Turno.objects.all().count(), turnos_count_inicial)

    def test_guardar_truno_error_medico_de_licencia(self):
        self.assertEqual(PeriodoSinAtencion.objects.all().count(), 0)
        turnos_count_inicial = Turno.objects.all().count()

        PeriodoSinAtencion.objects.create(fecha_inicio=datetime.today().date(), fecha_fin=datetime.today().date(),
                                          medico_id=1)
        data = self.turno_data
        data['hora_inicio'] = '12:00'
        data['hora_fin_estimada'] = '13:00'
        data['fecha_turno'] = datetime.today().date()

        response = self.client.get('/turno/guardar/', data)

        self.assertContains(response, '{"status": 0, "message": "El medico no atiende en la fecha seleccionada"}')
        self.assertEqual(Turno.objects.all().count(), turnos_count_inicial)

    def test_guardar_truno_error_fecha_turno_es_feriado(self):
        self.assertEqual(PeriodoSinAtencion.objects.all().count(), 0)
        turnos_count_inicial = Turno.objects.all().count()

        PeriodoSinAtencion.objects.create(fecha_inicio=datetime.today().date(), fecha_fin=datetime.today().date(),
                                          medico=None)
        data = self.turno_data
        data['hora_inicio'] = '12:00'
        data['hora_fin_estimada'] = '13:00'
        data['fecha_turno'] = datetime.today().date()

        response = self.client.get('/turno/guardar/', data)

        self.assertContains(response, '{"status": 0, "message": "El medico no atiende en la fecha seleccionada"}')
        self.assertEqual(Turno.objects.all().count(), turnos_count_inicial)


class IsFeriadoTest(TestCase):

    def setUp(self):
        self.today = datetime.today().date()
        self.fecha_inicio_feriado = self.today + timedelta(days=1)
        self.fecha_fin_feriado = self.today + timedelta(days=3)

        PeriodoSinAtencion.objects.create(fecha_inicio=self.fecha_inicio_feriado,
                                          fecha_fin=self.fecha_fin_feriado,
                                          medico_id=None)

    def test_que_no_es_feriado_con_fecha_antes_inicio_feriado(self):
        self.assertTrue(self.today < self.fecha_inicio_feriado)
        self.assertFalse(_is_feriado(self.today))

    def test_que_es_feriado_con_fecha_igual_a_inicio_feriado(self):
        self.assertTrue(_is_feriado(self.fecha_inicio_feriado))

    def test_que_es_feriado_con_fecha_igual_fin_feriado(self):
        self.assertTrue(_is_feriado(self.fecha_fin_feriado))

    def test_que_es_feriado_con_fecha_entre_inicio_y_fin_feriado(self):
        fecha = self.fecha_inicio_feriado + timedelta(days=1)
        self.assertTrue(self.fecha_inicio_feriado < fecha < self.fecha_fin_feriado)
        self.assertTrue(_is_feriado(fecha))

    def test_que_no_es_feriado_con_fecha_despues_de_finalizado_feriado(self):
        fecha = self.fecha_fin_feriado + timedelta(days=1)
        self.assertFalse(_is_feriado(fecha))


class IsMedicoDeLicenciaTest(TestCase):

    fixtures = ['medicos.json']

    def setUp(self):
        self.today = datetime.today().date()
        self.fecha_inicio_licencia = self.today + timedelta(days=1)
        self.fecha_fin_licencia = self.today + timedelta(days=3)
        self.medico = Medico.objects.get(pk=1)

        PeriodoSinAtencion.objects.create(fecha_inicio=self.fecha_inicio_licencia,
                                          fecha_fin=self.fecha_fin_licencia,
                                          medico=self.medico)

    def test_medico_no_esta_de_licencia_con_fecha_antes_inicio_licencia(self):
        self.assertTrue(self.today < self.fecha_inicio_licencia)
        self.assertFalse(_is_medico_con_licencia(self.today, self.medico.id))

    def test_medico_esta_de_licencia_con_fecha_igual_inicio_licencia(self):
        self.assertTrue(_is_medico_con_licencia(self.fecha_inicio_licencia, self.medico.id))

    def test_medico_esta_de_licencia_con_fecha_igual_fin_licencia(self):
        self.assertTrue(_is_medico_con_licencia(self.fecha_fin_licencia, self.medico.id))

    def test_medico_no_esta_de_licencia_con_fecha_entre_inicio_y_fin_licencia(self):
        fecha = self.fecha_inicio_licencia + timedelta(days=1)
        self.assertTrue(self.fecha_inicio_licencia < fecha < self.fecha_fin_licencia)
        self.assertTrue(_is_medico_con_licencia(fecha, self.medico.id))

    def test_medico_no_esta_de_licencia_con_fecha_despues_de_finalizada_la_licencia(self):
        fecha = self.fecha_fin_licencia + timedelta(days=1)
        self.assertFalse(_is_medico_con_licencia(fecha, self.medico.id))

    def test_medico_no_esta_de_licencia_con_fecha_igual_licencia_de_otro_medico(self):
        otro_medico_id = 2
        self.assertNotEquals(self.medico.id, otro_medico_id)
        self.assertFalse(_is_medico_con_licencia(self.fecha_inicio_licencia, otro_medico_id))
