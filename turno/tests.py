# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION, CHANGE

from turno.views import _is_feriado, _is_medico_con_licencia
from estudio.models import Estudio
from turno.models import Turno, PeriodoSinAtencion, Estado
from medico.models import Medico


class TurnosTest(TestCase):
    fixtures = ['anestesistas.json', 'turnos.json', 'pacientes.json', 'medicos.json',
                'practicas.json', 'obras_sociales.json', 'comprobantes.json', 'presentaciones.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
        self.turno_data = {'hora_inicio': '12:00', 'hora_fin_estimada': '13:00',
                           'fecha_turno': datetime.today().date(), 'id-sala': 1, 'id-paciente': 1, 'id-medico': 1,
                           'id-obra-social': 1, 'observacion_turno': 'test'}

    def test_anunciar_turno(self):
        """
        Deberia crear un estudio por cada practica del turno.
        """
        self.assertEqual(Estudio.objects.all().count(), 0)
        turno = Turno.objects.get(pk=1)

        response = self.client.post('/turno/1/anunciar/', {})
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == True
        assert content["message"] == "Success"
        self.assertEqual(Estudio.objects.all().count(), turno.practicas.all().count())

    def test_anunciar_crea_logs_por_cada_estudio_creado_y_uno_para_el_anunciar(self):
        ct_turno = ContentType.objects.get_for_model(Turno)
        ct_estudio = ContentType.objects.get_for_model(Estudio)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk).count(), 0)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_estudio.pk).count(), 0)
        self.assertEqual(Estudio.objects.all().count(), 0)
        turno = Turno.objects.get(pk=1)

        response = self.client.post('/turno/1/anunciar/', {})
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == True
        assert content["message"] == "Success"

        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk, action_flag=CHANGE).count(), 1)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_estudio.pk, action_flag=ADDITION).count(), turno.practicas.all().count())

    def test_anunciar_actualiza_el_public_id_del_estudio_por_uno_mas_corto_que_el_original(self):
        self.assertEqual(Estudio.objects.all().count(), 0)
        turno = Turno.objects.get(pk=1)

        response = self.client.post('/turno/1/anunciar/', {})
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == True
        assert content["message"] == "Success"
        self.assertEqual(Estudio.objects.all().count(), turno.practicas.all().count())
        estudio = Estudio.objects.all().first()
        self.assertNotEqual(estudio.public_id, '')
        self.assertTrue(len(estudio.public_id) < 10)  # universal is 32

    def test_guardar_truno_success(self):
        ct_turno = ContentType.objects.get_for_model(Turno)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk).count(), 0)

        turnos_count_inicial = Turno.objects.all().count()
        response = self.client.get('/turno/guardar/', self.turno_data)
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 1
        assert content["message"] == "El turno se ha creado correctamente."
        self.assertEqual(Turno.objects.all().count(), turnos_count_inicial + 1)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk, action_flag=ADDITION).count(), 1)

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
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 0
        assert content["message"] == 'Error, se ha detectado superposici\xf3n de turnos. Por favor, haga click en Mostrar y vuelva a intentarlo.'
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
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 0
        assert content["message"] == "El medico no atiende en la fecha seleccionada"
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
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 0
        assert content["message"] == "El medico no atiende en la fecha seleccionada"
        self.assertEqual(Turno.objects.all().count(), turnos_count_inicial)

    def test_modificar_turno_existente_success(self):
        ct_turno = ContentType.objects.get_for_model(Turno)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk).count(), 0)

        turno = Turno.objects.get(pk=1)
        turno.obraSocial.id = 1
        turno.observacion = 'test'
        turno.save()

        response = self.client.get('/turno/1/actualizar/', {'observacion': 'otra cosa', 'id-obra-social': 2})
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 1
        assert content["message"] == "El turno se ha guardado correctamente."

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.obraSocial.id, 2)
        self.assertEqual(turno.observacion, 'otra cosa')
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk, action_flag=CHANGE, object_id=turno.id).count(), 1)

    def test_anular_turno_success(self):
        ct_turno = ContentType.objects.get_for_model(Turno)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk).count(), 0)

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.estado.id, Estado.PENDIENTE)

        response = self.client.get('/turno/1/anular/', {'observacion_turno': 'descripcion anulacion'})
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 1
        assert content["message"] == "El turno se ha anulado correctamente."

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.estado.id, Estado.ANULADO)
        self.assertEqual(turno.observacion, 'descripcion anulacion')
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk, action_flag=CHANGE, object_id=turno.id).count(), 1)

    def test_reprogramar_turno_success(self):
        ct_turno = ContentType.objects.get_for_model(Turno)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk).count(), 0)

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.estado.id, Estado.PENDIENTE)

        response = self.client.get('/turno/1/reprogramar/', {'observacion_turno': 'descripcion anulacion'})

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.estado.id, Estado.ANULADO)
        self.assertEqual(turno.observacion, 'descripcion anulacion')
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk, action_flag=CHANGE, object_id=turno.id).count(), 1)

    def test_confirmar_turno_success(self):
        ct_turno = ContentType.objects.get_for_model(Turno)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk).count(), 0)

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.estado.id, Estado.PENDIENTE)

        response = self.client.get('/turno/1/confirmar/', {})
        assert response.content
        content = json.loads(response.content)
        assert content["status"] == 1
        assert content["message"] == "El turno se ha confirmado correctamente."

        turno = Turno.objects.get(pk=1)
        self.assertEqual(turno.estado.id, Estado.CONFIRMADO)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct_turno.pk, action_flag=CHANGE, object_id=turno.id).count(), 1)

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
        self.assertNotEqual(self.medico.id, otro_medico_id)
        self.assertFalse(_is_medico_con_licencia(self.fecha_inicio_licencia, otro_medico_id))
