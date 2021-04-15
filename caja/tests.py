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
    fixtures = ['caja.json', 'medicos.json', 'pacientes.json', 'practicas.json', 'obras_sociales.json',
        'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', 'medicamentos.json']
    
    def setUp(self):
        self.user = User.objects.create_user(username='walter', password='xx11', is_superuser=True)
        self.client = Client(HTTP_POST='localhost')
        self.client.login(username='walter', password='xx11')

        self.estudio_id = Estudio.objects.first().id
        self.cantidad_movimientos = MovimientoCaja.objects.count()
        self.ultimo_monto = MovimientoCaja.objects.last().monto_acumulado

        self.montos = ['10.00', '1.99']
        self.conceptos = ['qwerty', 'wasd']
        self.tipos_id = [TipoMovimientoCaja.objects.first().id, TipoMovimientoCaja.objects.last().id]
        self.medicos_id = [Medico.objects.first().id, Medico.objects.last().id]

        self.movimientos = [
            {
                'concepto': self.conceptos[0],
                'tipo_id': self.tipos_id[0],
                'medico_id': self.medicos_id[0],
                'monto': self.montos[0],
            },
            {
                'concepto': self.conceptos[1],
                'tipo_id': self.tipos_id[1],
                'medico_id': self.medicos_id[1],
                'monto': self.montos[1],
            }
        ]
    
    def test_crear_un_movimiento_funciona(self):
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': [
                self.movimientos[0]
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        nuevo_movimiento = MovimientoCaja.objects.last()

        assert response.status_code == status.HTTP_201_CREATED
        assert self.cantidad_movimientos + 1 == MovimientoCaja.objects.count()

        assert nuevo_movimiento.monto_acumulado == self.ultimo_monto + Decimal(self.montos[0])
        assert nuevo_movimiento.estudio.id == self.estudio_id
        assert nuevo_movimiento.medico.id == self.medicos_id[0]
        assert nuevo_movimiento.tipo.id == self.tipos_id[0]

    def test_crear_movimientos_funciona(self):
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': self.movimientos,
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        assert self.cantidad_movimientos + 2 == MovimientoCaja.objects.count()

        monto =  self.ultimo_monto + Decimal(self.montos[0]) + Decimal(self.montos[1])
        assert MovimientoCaja.objects.last().monto_acumulado == monto

    def test_crear_movimiento_funciona_con_monto_negativo(self):
        monto_negativo = '-1.22'
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': [
                self.movimientos[0],
                {
                    **self.movimientos[1],
                    'monto': monto_negativo,
                }
            ]
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        assert self.cantidad_movimientos + 2 == MovimientoCaja.objects.count()

        monto =  self.ultimo_monto + Decimal(self.montos[0]) + Decimal(monto_negativo)
        assert MovimientoCaja.objects.last().monto_acumulado == monto

    def test_crear_movimiento_funciona_sin_algunos_campos(self):
        datos = {
            'estudio_id': '',
            'movimientos': [
                {
                    **self.movimientos[0],
                    'concepto': '',
                    'medico_id': '',
                },
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        assert self.cantidad_movimientos + 1 == MovimientoCaja.objects.count()
        
        nuevo_movimiento = MovimientoCaja.objects.last()
        assert nuevo_movimiento.estudio == None
        assert nuevo_movimiento.medico == None
        assert nuevo_movimiento.concepto == ''

    def test_crear_movimientos_falla_sin_monto(self):
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': [
                {
                    **self.movimientos[0],
                    'monto': '',
                },
                self.movimientos[1],
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()

    def test_crear_movimientos_falla_monto_nulo(self):
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': [
                self.movimientos[0],
                {
                    **self.movimientos[1],
                    'monto': '0.00',
                }
            ],
        }
        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()
        
    def test_crear_movimientos_falla_con_tipo_erroneo(self):
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': [
                self.movimientos[0],
                {
                    **self.movimientos[1],
                    'medico_id': 'a',
                }
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()

        datos['estudio_id'] = 'a'
        datos['movimientos'][1]['medico_id'] =  self.medicos_id[1]

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()

        datos['estudio_id'] = self.estudio_id
        datos['movimientos'][1]['tipo_id'] = 'a'

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()

        datos['movimientos'][1]['tipo_id'] = self.tipos_id[1]
        datos['movimientos'][1]['monto'] = 'a'

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()

    def test_crear_movimientos_falla_sin_tipo(self):
        datos = {
            'estudio_id': self.estudio_id,
            'movimientos': [
                self.movimientos[0],
                {
                    **self.movimientos[1],
                    'tipo_id': '',
                }
            ],
        }

        response = self.client.post('/api/caja/', data=json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.cantidad_movimientos == MovimientoCaja.objects.count()

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
