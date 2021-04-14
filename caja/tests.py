# pylint: disable=no-name-in-module, import-error
import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from datetime import date

from caja.models import MovimientoCaja, TipoMovimientoCaja
from caja.serializers import MovimientoCajaImprimirSerializer
from medico.models import Medico
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
        results = json.loads(response.content).get('results')
        self.assertEqual(len(results), MovimientoCaja.objects.all().count())

    def test_filtro_concepto_funciona(self):
        parametro_busqueda = 'ingreso'
        response = self.client.get('/api/caja/?concepto={0}'.format(parametro_busqueda))
        results = json.loads(response.content).get('results')

        for result in results:
            assert parametro_busqueda in result['concepto']

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.exclude(concepto__contains=parametro_busqueda).count() == len(results)

    def test_filtro_medico_funciona(self):
        parametro_busqueda = '1'
        response = self.client.get('/api/caja/?medico={0}'.format(parametro_busqueda))
        results = json.loads(response.content).get('results')

        for result in results:
            assert result['medico']['id'] == int(parametro_busqueda)

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.exclude(medico__id=parametro_busqueda).count() == len(results)

    def test_filtro_fecha_funciona(self):
        fecha_inicial = '2019-02-01'
        fecha_final = '2019-02-08'
        response = self.client.get('/api/caja/?fecha_desde={0}&fecha_hasta={1}'.format(fecha_inicial, fecha_final))
        results = json.loads(response.content).get('results')

        for result in results:
            fecha = list(map(int, result['fecha'].split('-')))
            assert fecha[0] == 2019
            assert fecha[1] == 2
            assert 1 <= fecha[2] <= 8

    def test_filtro_tipo_movimiento_funciona(self):
        parametro_busqueda = 'General'
        response = self.client.get('/api/caja/?tipo_movimiento={0}'.format(parametro_busqueda))
        results = json.loads(response.content).get('results')

        for result in results:
            assert parametro_busqueda == result['tipo']['descripcion']

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.exclude(tipo__descripcion=parametro_busqueda).count() == len(results)

    def test_filtro_estudio_funciona(self):
        parametro_busqueda = 'True'
        response = self.client.get('/api/caja/?incluir_estudio={0}'.format(parametro_busqueda))
        results = json.loads(response.content).get('results')

        for result in results:
            assert result['estudio'] is not None

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.filter(estudio__isnull=strtobool(parametro_busqueda)).count() == len(results)

        parametro_busqueda = 'False'
        response = self.client.get('/api/caja/?incluir_estudio={0}'.format(parametro_busqueda))
        results = json.loads(response.content).get('results')

        for result in results:
            assert result['estudio'] is None

        assert MovimientoCaja.objects.count() - MovimientoCaja.objects.filter(estudio__isnull=strtobool(parametro_busqueda)).count() == len(results)


class ImprimirCajaTest(TestCase):
    fixtures = ['caja.json', 'medicos.json', 'pacientes.json', 'practicas.json', 'obras_sociales.json',
        'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', 'medicamentos.json']

    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')

    def test_serializer_funciona(self):
        movimientos = MovimientoCaja.objects.all()
        movimientos_serializer = MovimientoCajaImprimirSerializer(movimientos, many=True).data

        assert movimientos.count() == len(movimientos_serializer)

        for mov, mov_serializer in zip(movimientos, movimientos_serializer):
            assert str(mov.monto) == mov_serializer['monto']
            assert str(mov.monto_acumulado) == mov_serializer['monto_acumulado']
            assert mov.hora == mov_serializer['hora']
            assert mov.concepto == mov_serializer['concepto']
            assert str(mov.tipo) == mov_serializer['tipo']
            
            medico = mov.medico
            if mov.estudio:
                assert str(mov.estudio.obra_social) == mov_serializer['obra_social']
                assert str(mov.estudio.practica) == mov_serializer['practica']
                medico = medico or mov.estudio.medico
            
            if medico:
                assert str(medico) == mov_serializer['medico']

    def test_serializer_rellena_los_campos_opcionales(self):
        movimiento = MovimientoCaja(concepto='', fecha=date.today(), hora='00:00', tipo=TipoMovimientoCaja.objects.first())
        movimiento_serializer = MovimientoCajaImprimirSerializer(movimiento).data

        assert movimiento_serializer['concepto'] == ''
        assert movimiento_serializer['paciente'] == ''
        assert movimiento_serializer['obra_social'] == ''
        assert movimiento_serializer['medico'] == ''
        assert movimiento_serializer['practica'] == ''

    def test_serializer_elige_el_medico_correctamente(self):
        movimiento = MovimientoCaja.objects.first()
        medico = Medico.objects.first()
        medico_estudio = Medico.objects.get(pk=2)

        assert medico != medico_estudio

        movimiento.medico = medico
        movimiento_serializer = MovimientoCajaImprimirSerializer(movimiento).data
        assert movimiento_serializer['medico'] == str(medico)

        movimiento.medico = None
        movimiento.estudio = Estudio.objects.first()
        movimiento.estudio.medico = medico_estudio
        movimiento_serializer = MovimientoCajaImprimirSerializer(movimiento).data
        assert movimiento_serializer['medico'] == str(medico_estudio)

        movimiento.medico = medico
        movimiento_serializer = MovimientoCajaImprimirSerializer(movimiento).data

        assert movimiento_serializer['medico'] == str(medico)
