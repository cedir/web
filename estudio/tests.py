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

from estudio.models import ID_SUCURSAL_CEDIR, ID_SUCURSAL_HOSPITAL_ITALIANO

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


class ActualizarEstudiosTest(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json', 'anestesistas.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
        self.estudio_data = {'fecha': datetime.today().date(), 'paciente': 1, 'practica': 1, 'medico': 1,
                             'obra_social': 1, 'medico_solicitante': 1, 'anestesista': 1}

    def test_update_estudio_crea_log(self):
        ct = ContentType.objects.get_for_model(Estudio)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk).count(), 0)

        estudio = Estudio.objects.create(fecha=datetime.today().date(), paciente_id=1, practica_id=1, medico_id=1,
                                         obra_social_id=1, medico_solicitante_id=1, anestesista_id=1)

        self.estudio_data['fecha'] = '2019-03-07'
        response = self.client.put('/api/estudio/{}/'.format(estudio.id), data=json.dumps(self.estudio_data), content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertEqual(LogEntry.objects.filter(content_type_id=ct.pk, object_id=estudio.id, action_flag=CHANGE).count(), 1)


class UpdateImportesYPagoContraFacturaTests(TestCase):
    fixtures = ['comprobantes.json', 'pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
        self.url = '/api/estudio/{}'
        self.estudio = Estudio.objects.create(fecha=datetime.today().date(), paciente_id=1, practica_id=1, medico_id=1,
                                              obra_social_id=1, medico_solicitante_id=1, anestesista_id=1,
                                              pension=0, diferencia_paciente=0, arancel_anestesia=0)

    def test_importes_son_actualizados_correctamente(self):
        data = {'pension': '123', 'diferencia_paciente': '234', 'arancel_anestesia': '4543'}

        self.assertFalse(bool(self.estudio.presentacion_id))
        self.assertIsNone(self.estudio.fecha_cobro)
        self.assertFalse(self.estudio.es_pago_contra_factura)
        self.assertEqual(self.estudio.pago_contra_factura, Decimal(0))

        url = self.url + '/update_importes/'
        response = self.client.patch(url.format(self.estudio.id),
                                     data=json.dumps(data), content_type='application/json')

        self.assertEquals(response.status_code, 200)

        estudio = Estudio.objects.get(pk=self.estudio.id)
        self.assertEqual(estudio.pension, Decimal(data.get('pension')))
        self.assertEqual(estudio.diferencia_paciente, Decimal(data.get('diferencia_paciente')))
        self.assertEqual(estudio.arancel_anestesia, Decimal(data.get('arancel_anestesia')))
        self.assertFalse(bool(estudio.es_pago_contra_factura))
        self.assertEqual(estudio.pago_contra_factura, Decimal(0))

    @patch('estudio.views.Estudio.anular_pago_contra_factura')
    @patch('estudio.views.Estudio.set_pago_contra_factura')
    def test_pago_contra_factura_se_actualiza_si_el_importe_enviado_es_mayor_a_cero(self, set_pago_contra_factura_mock,
                                                                                    anular_pago_contra_factura_mock):
        data = {'pago_contra_factura': '5656'}

        self.assertFalse(bool(self.estudio.presentacion_id))
        self.assertIsNone(self.estudio.fecha_cobro)
        self.assertFalse(self.estudio.es_pago_contra_factura)
        self.assertEqual(self.estudio.pago_contra_factura, Decimal(0))

        url = self.url + '/realizar_pago_contra_factura/'
        response = self.client.put(url.format(self.estudio.id),
                                     data=json.dumps(data), content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertTrue(set_pago_contra_factura_mock.called)
        self.assertFalse(anular_pago_contra_factura_mock.called)

    @patch('estudio.views.Estudio.anular_pago_contra_factura')
    @patch('estudio.views.Estudio.set_pago_contra_factura')
    def test_pago_contra_factura_no_se_llama_si_el_importe_no_cambia(self, set_pago_contra_factura_mock,
                                                                     anular_pago_contra_factura_mock):
        importe_pcf = '200'
        data = {'pago_contra_factura': importe_pcf}

        self.assertFalse(bool(self.estudio.presentacion_id))
        self.estudio.es_pago_contra_factura = 1
        self.estudio.pago_contra_factura = Decimal(importe_pcf)
        self.estudio.fecha_cobro = datetime.today()
        self.estudio.save()

        url = self.url + '/realizar_pago_contra_factura/'
        response = self.client.put(url.format(self.estudio.id),
                                     data=json.dumps(data), content_type='application/json')

        self.assertEquals(response.status_code, 400)
        self.assertFalse(set_pago_contra_factura_mock.called)
        self.assertFalse(anular_pago_contra_factura_mock.called)

    @patch('estudio.views.Estudio.anular_pago_contra_factura')
    @patch('estudio.views.Estudio.set_pago_contra_factura')
    def test_pago_contra_factura_se_anula(self, set_pago_contra_factura_mock,
                                                                        anular_pago_contra_factura_mock):
        self.assertFalse(bool(self.estudio.presentacion_id))
        self.estudio.es_pago_contra_factura = 1
        self.estudio.pago_contra_factura = Decimal('200')
        self.estudio.fecha_cobro = datetime.today()
        self.estudio.save()

        url = self.url + '/anular_pago_contra_factura/'
        response = self.client.put(url.format(self.estudio.id), content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertFalse(set_pago_contra_factura_mock.called)
        self.assertTrue(anular_pago_contra_factura_mock.called)

    def test_pago_contra_factura_devuelve_bad_request_si_falla_la_validacion(self):
        data = {'pago_contra_factura': '200'}

        self.estudio.presentacion = Presentacion.objects.get(pk=1)  # no se puede dar de pago contra factura si esta presentado
        self.estudio.save()

        url = self.url + '/realizar_pago_contra_factura/'
        response = self.client.put(url.format(self.estudio.id),
                                     data=json.dumps(data), content_type='application/json')

        self.assertEquals(response.status_code, 400)

    def test_pago_contra_factura_devuelve_bad_request_si_el_importe_es_negativo(self):
        data = {'pago_contra_factura': '-200'}
        self.assertFalse(bool(self.estudio.presentacion_id))
        self.assertIsNone(self.estudio.fecha_cobro)
        self.assertFalse(self.estudio.es_pago_contra_factura)
        self.assertEqual(self.estudio.pago_contra_factura, Decimal(0))

        url = self.url + '/realizar_pago_contra_factura/'
        response = self.client.put(url.format(self.estudio.id),
                                     data=json.dumps(data), content_type='application/json')

        self.assertEquals(response.status_code, 400)


class RetreiveEstudiosTest(TestCase):
    fixtures = ['comprobantes.json', 'pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
        self.estudio = Estudio.objects.create(fecha=datetime.today().date(), paciente_id=1, practica_id=1, medico_id=1,
                                              obra_social_id=1, medico_solicitante_id=1, anestesista_id=1, sucursal=1)
        self.estudio.presentacion = Presentacion.objects.get(pk=1)
        self.estudio.save()

    def test_response_payload_estado_es_descriptivo(self):
        response = self.client.get('/api/estudio/{}/'.format(self.estudio.id), content_type='application/json')

        payload = json.loads(response.content)
        self.assertEqual(payload.get('presentacion').get('estado'), 'Pendiente')

    def test_filtro_por_sucursal_funciona_si_sucursal_es_cedir(self):
        results = Estudio.objects.all()

        response = json.loads(self.client.get('/api/estudio/?sucursal={}'.format(ID_SUCURSAL_CEDIR), content_type='application/json').content)['results']

        for estudio in response:
            self.assertEqual(results[estudio['id'] - 1].sucursal, ID_SUCURSAL_CEDIR)

    def test_filtro_por_sucursal_funciona_si_sucursal_es_hospital_italiano(self):
        results = Estudio.objects.all()

        response = json.loads(self.client.get('/api/estudio/?sucursal={}'.format(ID_SUCURSAL_HOSPITAL_ITALIANO), content_type='application/json').content)['results']

        for estudio in response:
            self.assertEqual(results[estudio['id'] - 1].sucursal, ID_SUCURSAL_HOSPITAL_ITALIANO)

    def test_filtro_por_sucursal_devuelve_estudios_cedir_si_no_se_envia_sucursal(self):
        results = Estudio.objects.all()

        response = json.loads(self.client.get('/api/estudio/', content_type='application/json').content)['results']

        for estudio in response:
            self.assertEqual(results[estudio['id'] - 1].sucursal, ID_SUCURSAL_CEDIR)
