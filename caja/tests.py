# pylint: disable=no-name-in-module, import-error
import json
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from rest_framework import status

from medico.models import Medico
from caja.models import MovimientoCaja, TipoMovimientoCaja
from estudio.models import Estudio

from distutils.util import strtobool
from datetime import datetime, date
from decimal import Decimal

class CrearMovimientosTest(TestCase):
    fixtures = ['caja.json', 'medicos.json', 'pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
        'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', 'medicamentos.json']
    
    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')
    
    def test_crear_un_movimiento_funciona(self):
        medico_id = Medico.objects.all().first().id
        tipo_id = TipoMovimientoCaja.objects.all().first().id
        estudio_id = Estudio.objects.all().first().id
        cantidad_movimientos = len(MovimientoCaja.objects.all())
        monto = '10.00'
        ultimo_monto = MovimientoCaja.objects.all().last().monto_acumulado
        datos = {
            'estudio_id': estudio_id,
            'movimientos': [
                {
                    'concepto': 'ASD',
                    'tipo_id': tipo_id,
                    'medico_id': medico_id,
                    'monto': monto,
                },
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        nuevo_movimiento = MovimientoCaja.objects.all().last()

        assert response.status_code == status.HTTP_201_CREATED
        assert cantidad_movimientos + 1 == len(MovimientoCaja.objects.all())
        assert nuevo_movimiento.monto_acumulado == ultimo_monto + Decimal(monto)
        assert nuevo_movimiento.estudio == Estudio.objects.all().first()
        assert nuevo_movimiento.medico == Medico.objects.all().first()
        assert nuevo_movimiento.tipo == TipoMovimientoCaja.objects.all().first()

    def test_crear_movimientos_funciona(self):
        medico_id = Medico.objects.all().first().id, Medico.objects.all().last().id
        tipo_id = TipoMovimientoCaja.objects.all().first().id, TipoMovimientoCaja.objects.all().last().id
        estudio_id = Estudio.objects.all().first().id
        cantidad_movimientos = len(MovimientoCaja.objects.all())
        montos = '10.00', '-1.99'
        ultimo_monto = MovimientoCaja.objects.all().last().monto_acumulado
        datos = {
            'estudio_id': estudio_id,
            'movimientos': [
                {
                    'concepto': 'ASD',
                    'tipo_id': tipo_id[0],
                    'medico_id': medico_id[0],
                    'monto': montos[0],
                },
                {
                    'concepto': 'ASDasd',
                    'tipo_id': tipo_id[1],
                    'medico_id': medico_id[1],
                    'monto': montos[1],
                }
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        assert cantidad_movimientos + 2 == len(MovimientoCaja.objects.all())
        monto =  ultimo_monto + Decimal(montos[0]) + Decimal(montos[1])
        assert MovimientoCaja.objects.all().last().monto_acumulado == monto

    def test_crear_movimiento_funciona_sin_algunos_campos(self):
        tipo_id = TipoMovimientoCaja.objects.all().first().id
        cantidad_movimientos = len(MovimientoCaja.objects.all())
        monto = '10.00'
        ultimo_monto = MovimientoCaja.objects.all().last().monto_acumulado
        datos = {
            'estudio_id': '',
            'movimientos': [
                {
                    'concepto': '',
                    'tipo_id': tipo_id,
                    'medico_id': '',
                    'monto': monto,
                },
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')
        # print(response.content)

        assert response.status_code == status.HTTP_201_CREATED
        assert cantidad_movimientos + 1 == len(MovimientoCaja.objects.all())
        assert MovimientoCaja.objects.all().last().estudio == None
        assert MovimientoCaja.objects.all().last().medico == None
        assert MovimientoCaja.objects.all().last().concepto == ''

        def test_crear_movimientos_falla_sin_monto(self):
            medico_id = Medico.objects.all().first().id
            tipo_id = TipoMovimientoCaja.objects.all().first().id
            estudio_id = Estudio.objects.all().first().id
            cantidad_movimientos = len(MovimientoCaja.objects.all())
            monto = '10.00'
            ultimo_monto = MovimientoCaja.objects.all().last().monto_acumulado
            datos = {
                'estudio_id': estudio_id,
                'movimientos': [
                    {
                        'concepto': 'asd',
                        'tipo_id': tipo_id,
                        'medico_id': medico_id,
                        'monto': '',
                    },
                    {
                        'concepto': 'asd',
                        'tipo_id': tipo_id,
                        'medico_id': medico_id,
                        'monto': monto,
                    }
                ],
            }

            response = self.client.post('/api/caja/', data=json.dumps(datos),
                                    content_type='application/json')

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert cantidad_movimientos == len(MovimientoCaja.objects.all())
        
        def test_crear_movimientos_falla_sin_tipo(self):
            medico_id = Medico.objects.all().first().id
            tipo_id = TipoMovimientoCaja.objects.all().first().id
            estudio_id = Estudio.objects.all().first().id
            cantidad_movimientos = len(MovimientoCaja.objects.all())
            monto = '10.00'
            ultimo_monto = MovimientoCaja.objects.all().last().monto_acumulado
            datos = {
                'estudio_id': estudio_id,
                'movimientos': [
                    {
                        'concepto': 'asd',
                        'tipo_id': tipo_id,
                        'medico_id': medico_id,
                        'monto': '',
                    },
                    {
                        'concepto': 'asd',
                        'tipo_id': '',
                        'medico_id': medico_id,
                        'monto': monto,
                    }
                ],
            }

            response = self.client.post('/api/caja/', data=json.dumps(datos),
                                    content_type='application/json')

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert cantidad_movimientos == len(MovimientoCaja.objects.all())

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
