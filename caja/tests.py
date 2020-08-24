# pylint: disable=no-name-in-module, import-error
import simplejson
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from caja.models import MovimientoCaja
from estudio.models import Estudio
from distutils.util import strtobool


class ListadoCajaTest(TestCase):
    fixtures = ['caja.json', 'medicos.json', 'pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
        'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', 'medicamentos.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')

    def test_listado(self):
        response = self.client.get('/api/caja/', {})
        results = simplejson.loads(response.content).get('results')
        self.assertEquals(len(results), MovimientoCaja.objects.all().count())

    def test_filtro_concepto_funciona(self):
        parametro_busqueda = 'ingreso'
        response = self.client.get('/api/caja/?concepto={0}'.format(parametro_busqueda))
        results = simplejson.loads(response.content).get('results')

        for result in results:
            assert parametro_busqueda in result['concepto']

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.exclude(concepto__contains=parametro_busqueda).count() == len(results)

    def test_filtro_medico_funciona(self):
        parametro_busqueda = '1'
        response = self.client.get('/api/caja/?medico={0}'.format(parametro_busqueda))
        results = simplejson.loads(response.content).get('results')

        for result in results:
            assert result['medico']['id'] == int(parametro_busqueda)

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.exclude(medico__id=parametro_busqueda).count() == len(results)

    def test_filtro_fecha_funciona(self):
        fecha_inicial = '2019-02-01'
        fecha_final = '2019-02-08'
        response = self.client.get('/api/caja/?fecha_desde={0}&fecha_hasta={1}'.format(fecha_inicial, fecha_final))
        results = simplejson.loads(response.content).get('results')

        for result in results:
            fecha = map(int, result['fecha'].split('-'))
            assert fecha[0] == 2019
            assert fecha[1] == 2
            assert 1 <= fecha[2] <= 8

    def test_filtro_tipo_movimiento_funciona(self):
        parametro_busqueda = 'General'
        response = self.client.get('/api/caja/?tipo_movimiento={0}'.format(parametro_busqueda))
        results = simplejson.loads(response.content).get('results')

        for result in results:
            assert parametro_busqueda == result['tipo']['descripcion']

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.exclude(tipo__descripcion=parametro_busqueda).count() == len(results)

    def test_filtro_estudio_funciona(self):
        parametro_busqueda = 'True'
        response = self.client.get('/api/caja/?incluir_estudio={0}'.format(parametro_busqueda))
        results = simplejson.loads(response.content).get('results')

        for result in results:
            assert result['estudio'] is not None

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.filter(estudio__isnull=strtobool(parametro_busqueda)).count() == len(results)
        
        parametro_busqueda = 'False'
        response = self.client.get('/api/caja/?incluir_estudio={0}'.format(parametro_busqueda))
        results = simplejson.loads(response.content).get('results')

        for result in results:
            assert result['estudio'] is None

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.filter(estudio__isnull=strtobool(parametro_busqueda)).count() == len(results)
