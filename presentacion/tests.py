import json
from decimal import Decimal
from mock import patch
from datetime import date

from django.test import TestCase, Client
from django.contrib.auth.models import User

from presentacion.models import Presentacion
from obra_social.models import ObraSocial
from estudio.models import Estudio
from medico.models import Medico
from comprobante.models import Comprobante, ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO
from comprobante.afip import AfipError
from presentacion.obra_social_custom_code.amr_presentacion_digital import AmrRowBase
from presentacion.obra_social_custom_code.osde_presentacion_digital import OsdeRowBase

class TestDetallesObrasSociales(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_detalle_osde(self):
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.fecha_cobro = None
        presentacion.save()
        response = self.client.get('/api/presentacion/1/get_detalle_osde/')
        assert response.content != ''

    def test_detalle_amr(self):
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.fecha_cobro = None
        presentacion.save()
        response = self.client.get('/api/presentacion/1/get_detalle_amr/')
        assert response.content != ''

    def test_detalle_amr_no_posee_caracter_de_nueva_linea_y_barra_invertida_al_final(self):
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.fecha_cobro = None
        presentacion.save()
        response = self.client.get('/api/presentacion/1/get_detalle_amr/')
        assert response.content[-1] != '\\'
        assert response.content[-1] != '\n'

    def test_cobrar_osde_en_nombre_de_otro_medico(self):
        estudio_osde = Estudio.objects.get(pk=1)
        presentacion_osde = OsdeRowBase(estudio_osde)

        medico = Medico.objects.get(pk=2)

        assert presentacion_osde.format_nro_matricula(medico) == '0000000333'

        medico_para_facturar_osde = Medico.objects.get(pk=1)

        medico.facturar_osde_en_nombre_de_medico = medico_para_facturar_osde
        assert presentacion_osde.format_nro_matricula(medico) == '0000000222'

    def test_cobrar_amr_en_nombre_de_otro_medico(self):
        estudio_amr = Estudio.objects.get(pk=1)
        comp = Comprobante.objects.get(pk=1)
        presentacion_amr = AmrRowBase(estudio_amr, comp)

        medico = Medico.objects.get(pk=2)

        assert presentacion_amr.format_nro_matricula(medico) == 333

        medico_para_facturar_amr = Medico.objects.get(pk=1)

        medico.facturar_amr_en_nombre_de_medico = medico_para_facturar_amr
        assert presentacion_amr.format_nro_matricula(medico) == 222

class TestRetrievePresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_listar_presentaciones_ok(self):
        response = self.client.get('/api/presentacion/')
        assert response.status_code == 200

    def test_detalles_presentacion_ok(self):
        response = self.client.get('/api/presentacion/1/')
        assert response.status_code == 200

class TestCobrarPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_cobrar_presentacion_ok(self):
        presentacion = Presentacion.objects.get(pk=7)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante.estado == Comprobante.NO_COBRADO
        datos = {
            "estudios": [
                {
                    "id": 8,
                    "importe_cobrado_pension": "1.00",
                    "importe_cobrado_arancel_anestesia": "1.00",
                    "importe_estudio_cobrado": "1.00",
                    "importe_medicacion_cobrado": "1.00",
                },
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/7/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=7)
        assert presentacion.estado == Presentacion.COBRADO
        assert presentacion.comprobante.estado == Comprobante.COBRADO
        assert presentacion.pago != None

    def test_cobrar_presentacion_devuelve_diferencia_con_facturado(self):
        # diferencia facturada: cobrados - (facturados - diferencia_paciente)
        presentacion = Presentacion.objects.get(pk=7)
        presentacion.total_facturado = Decimal(5)
        presentacion.save()
        datos = {
            "estudios": [
                {
                    "id": 8,
                    "importe_cobrado_pension": "1.00",
                    "importe_cobrado_arancel_anestesia": "1.00",
                    "importe_estudio_cobrado": "1.00",
                    "importe_medicacion_cobrado": "1.00",
                },
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/7/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=7)
        assert Decimal(json.loads(response.content)["diferencia_facturada"]) == Decimal(1)

    def test_cobrar_presentacion_setea_valores(self):
        # diferencia facturada: cobrados - (facturados - diferencia_paciente)
        presentacion = Presentacion.objects.get(pk=7)
        estudio = Estudio.objects.get(pk=8)
        assert estudio.importe_estudio_cobrado == Decimal(0)
        assert estudio.importe_medicacion_cobrado == Decimal(0)
        assert estudio.importe_cobrado_pension == Decimal(0)
        assert estudio.importe_cobrado_arancel_anestesia == Decimal(0)
        estudio.importe_cobrado_arancel_anestesia = Decimal(1)
        datos = {
            "estudios": [
                {
                    "id": 8,
                    "importe_cobrado_pension": "1.00",
                    "importe_cobrado_arancel_anestesia": "1.00",
                    "importe_estudio_cobrado": "1.00",
                    "importe_medicacion_cobrado": "1.00",
                },
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/7/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 200
        estudio = Estudio.objects.get(pk=8)
        presentacion = Presentacion.objects.get(pk=7)
        pago = presentacion.pago.get()
        assert estudio.importe_estudio_cobrado == Decimal(1)
        assert estudio.importe_medicacion_cobrado == Decimal(1)
        assert estudio.importe_cobrado_pension == Decimal(1)
        assert estudio.importe_cobrado_arancel_anestesia == Decimal(1)
        assert presentacion.total_cobrado == Decimal(4)
        assert pago.importe == presentacion.total_cobrado
        assert pago.nro_recibo == "1"
        assert pago.fecha == date.today()
        assert pago.retencion_impositiva == Decimal("32.00")

    def test_cobrar_presentacion_abierta_falla(self):
        presentacion = Presentacion.objects.get(pk=8)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.ABIERTO
        datos = {
            "estudios": [
                {
                    "id": 11,
                    "importe_cobrado_pension": "1.00",
                    "importe_cobrado_arancel_anestesia": "1.00",
                    "importe_estudio_cobrado": "1.00",
                    "importe_medicacion_cobrado": "1.00",
                },
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/8/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 400
        presentacion = Presentacion.objects.get(pk=8)
        assert presentacion.estado == Presentacion.ABIERTO
        assert presentacion.comprobante.estado == Comprobante.NO_COBRADO

    def test_cobrar_presentacion_cobrada_falla(self):
        presentacion = Presentacion.objects.get(pk=2)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.COBRADO
        datos = {
            "estudios": [
                {
                    "id": 2,
                    "importe_cobrado_pension": "1.00",
                    "importe_cobrado_arancel_anestesia": "1.00",
                    "importe_estudio_cobrado": "1.00",
                    "importe_medicacion_cobrado": "1.00",
                },
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/2/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 400
        presentacion = Presentacion.objects.get(pk=2)
        assert presentacion.estado == Presentacion.COBRADO
        assert presentacion.comprobante.estado == Comprobante.COBRADO

    def test_cobrar_presentacion_estudio_no_es_de_la_presentacion_falla(self):
        presentacion = Presentacion.objects.get(pk=7)
        estudio = Estudio.objects.get(pk=9)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.PENDIENTE
        assert estudio.presentacion != presentacion
        datos = {
            "estudios": [
                {
                    "id": 9,
                    "importe_cobrado_pension": "1.00",
                    "importe_cobrado_arancel_anestesia": "1.00",
                    "importe_estudio_cobrado": "1.00",
                    "importe_medicacion_cobrado": "1.00",
                },
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/7/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 400
        presentacion = Presentacion.objects.get(pk=7)
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante.estado == Comprobante.NO_COBRADO

    def test_cobrar_presentacion_faltan_estudios_falla(self):
        presentacion = Presentacion.objects.get(pk=7)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.PENDIENTE
        datos = {
            "estudios": [
            ],
            "retencion_impositiva": "32.00",
            "nro_recibo": 1,
        }
        response = self.client.patch('/api/presentacion/7/cobrar/', data=json.dumps(datos),
                                     content_type='application/json')
        assert response.status_code == 400
        presentacion = Presentacion.objects.get(pk=7)
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante.estado == Comprobante.NO_COBRADO

class TestEstudiosDePresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
    'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_get_estudios_de_presentacion(self):
        presentacion = Presentacion.objects.get(pk=1)
        n_estudios = len(presentacion.estudios.all())
        assert n_estudios != 0
        response = self.client.get('/api/presentacion/1/estudios/')
        estudios_response = json.loads(response.content)
        assert len(estudios_response) == n_estudios

class TestCrearPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_crear_presentacion_ok(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 201
        presentacion = Presentacion.objects.get(pk=json.loads(response.content)['id'])
        assert presentacion.estado == Presentacion.ABIERTO
        assert presentacion.comprobante is None

    def test_crear_presentacion_actualiza_estudios(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        assert estudio.importe_estudio == Decimal("10000.00")
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        estudio = Estudio.objects.get(pk=9)
        assert estudio.presentacion_id != 0
        assert estudio.importe_estudio == 5

    def test_crear_presentacion_con_estudio_ya_presentado_falla(self):
        estudio_ya_presentado = Estudio.objects.get(pk=1)
        assert estudio_ya_presentado.presentacion_id != 0
        datos = {
            "obra_social_id": 1,
            "periodo": "perio2",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 1,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

    def test_crear_presentacion_con_estudio_obra_social_distinta_falla(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.presentacion_id == 0
        assert estudio.obra_social_id == 1
        datos = {
            "obra_social_id": 5,
            "periodo": "perio2",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

    def test_crear_presentacion_estudio_queda_asociado(self):
        estudio = Estudio.objects.get(pk=9)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        estudio = Estudio.objects.get(pk=9)
        assert estudio.presentacion_id == response.data['id']

    def test_crear_presentacion_total_es_suma_importes_estudios(self):
        datos = {
            "obra_social_id": 1,
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 1,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ]
        }

        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        presentacion = Presentacion.objects.get(pk=response.data['id'])
        assert presentacion.total_facturado == 3

    def test_crear_presentacion_falla_si_estudio_es_de_otra_sucursal(self):
        estudio = Estudio.objects.get(pk=9)
        estudio.sucursal = 2
        estudio.save()
        assert estudio.presentacion_id == 0
        datos = {
            "obra_social_id": 5,
            "periodo": "perio2",
            "fecha": "2019-12-25",
            "sucursal": 1,
            "estudios": [
                {
                    "id": 9,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ],
        }
        response = self.client.post('/api/presentacion/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

class TestUpdatePresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    def test_update_presentacion_ok(self):
        # Tomamos una presentacion con dos estudios, quitamos uno y agregamos otro.
        # Tambien cambiamos valores.
        presentacion = Presentacion.objects.get(pk=8)
        estudio_1 = Estudio.objects.get(pk=10)
        estudio_2 = Estudio.objects.get(pk=11)
        estudio_3 = Estudio.objects.get(pk=12)
        assert presentacion.estado == Presentacion.ABIERTO
        assert presentacion.fecha == date(2012, 7, 6)
        assert presentacion.periodo == "perio2"
        assert estudio_1.presentacion == presentacion
        assert estudio_2.presentacion == presentacion
        assert estudio_3.presentacion_id == 0
        assert presentacion.estudios.count() == 2

        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 11,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ]
        }

        response = self.client.patch('/api/presentacion/8/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=8)
        estudio_1 = Estudio.objects.get(pk=10)
        estudio_2 = Estudio.objects.get(pk=11)
        estudio_3 = Estudio.objects.get(pk=12)
        assert presentacion.fecha == date(2019, 12, 25)
        assert presentacion.periodo == "perio3"
        assert estudio_1.presentacion_id == 0
        assert estudio_2.presentacion == presentacion
        assert estudio_3.presentacion == presentacion
        assert presentacion.estudios.count() == 2

    def test_update_presentacion_actualiza_estudios(self):
        presentacion = Presentacion.objects.get(pk=8)
        estudio = Estudio.objects.get(pk=12)
        assert estudio.obra_social_id == 1
        assert estudio.presentacion_id == 0
        assert estudio.importe_estudio == Decimal("10000.00")
        datos = {
            "obra_social_id": 1,
            "periodo": "SEPTIEMBRE 2019",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
            ],
        }
        response = self.client.patch('/api/presentacion/8/', data=json.dumps(datos),
                                content_type='application/json')
        estudio = Estudio.objects.get(pk=12)
        assert estudio.presentacion_id != 0
        assert estudio.importe_estudio == 5

    def test_update_presentacion_cerrada_falla(self):
        # Tomamos una presentacion con dos estudios, quitamos uno y agregamos otro.
        # Tambien cambiamos valores.
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.PENDIENTE
        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 11,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ]
        }

        response = self.client.patch('/api/presentacion/1/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

        presentacion = Presentacion.objects.get(pk=2)
        assert presentacion.estado == Presentacion.COBRADO
        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 11,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ]
        }

        response = self.client.patch('/api/presentacion/2/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

    def test_update_presentacion_con_estudio_obra_social_distinta_falla(self):
        estudio = Estudio.objects.get(pk=12)
        presentacion = Presentacion.objects.get(pk=9)
        assert estudio.presentacion_id == 0
        assert estudio.obra_social_id == 1
        assert presentacion.obra_social_id == 5
        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
            ]
        }
        response = self.client.patch('/api/presentacion/9/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

    def test_update_presentacion_con_estudio_ya_presentado_falla(self):
        estudio_ya_presentado = Estudio.objects.get(pk=1)
        assert estudio_ya_presentado.presentacion_id != 0
        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 1,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
            ]
        }
        response = self.client.patch('/api/presentacion/8/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

    def test_update_presentacion_total_es_suma_importes_estudios(self):
        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 1,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                }
            ]
        }

        response = self.client.patch('/api/presentacion/8/', data=json.dumps(datos),
                                content_type='application/json')
        presentacion = Presentacion.objects.get(pk=8)
        assert presentacion.total_facturado == 3

    def test_update_presentacion_con_estudio_de_otra_sucursal_falla(self):
        estudio = Estudio.objects.get(pk=12)
        estudio.sucursal = 2
        estudio.save()
        presentacion = Presentacion.objects.get(pk=9)
        assert estudio.presentacion_id == 0
        assert presentacion.sucursal == 1
        datos = {
            "periodo": "perio3",
            "fecha": "2019-12-25",
            "estudios": [
                {
                    "id": 12,
                    "nro_de_orden": "FE003450603",
                    "importe_estudio": 5,
                    "pension": 1,
                    "diferencia_paciente": 1,
                    "medicacion": 1,
                    "arancel_anestesia": 1
                },
            ]
        }
        response = self.client.patch('/api/presentacion/9/', data=json.dumps(datos),
                                content_type='application/json')
        assert response.status_code == 400

class TestAbrirPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json', 'obras_sociales.json',
                'anestesistas.json', 'presentaciones.json', 'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    @patch('comprobante.comprobante_asociado.Afip')
    def test_abrir_presentacion_ok(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10

        presentacion = Presentacion.objects.get(pk=1)
        pk_comprobante_viejo = presentacion.comprobante.pk
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_FACTURA
        assert presentacion.comprobante.estado == Comprobante.NO_COBRADO
        response = self.client.patch('/api/presentacion/1/abrir/')
        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.ABIERTO
        assert Comprobante.objects.get(pk=pk_comprobante_viejo).estado == Comprobante.ANULADO
        assert presentacion.comprobante == None

    @patch('comprobante.comprobante_asociado.Afip')
    def test_abrir_presentacion_no_pendiente_falla(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        response = self.client.patch('/api/presentacion/1/abrir/')
        assert response.status_code == 400
        assert presentacion.estado == Presentacion.ABIERTO

        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.COBRADO
        presentacion.save()
        response = self.client.patch('/api/presentacion/1/abrir/')
        assert response.status_code == 400
        assert presentacion.estado == Presentacion.COBRADO
        assert not afip.emitir_comprobante.called

class TestCerrarPresentacion(TestCase):
    fixtures = ['pacientes.json', 'medicos.json', 'practicas.json',
                'obras_sociales.json', 'anestesistas.json', 'presentaciones.json',
                'comprobantes.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        self.client = Client(HTTP_GET='localhost')
        self.client.login(username='test', password='test')

    @patch('comprobante.serializers.Afip')
    def test_cerrar_presentacion_con_factura_ok(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.comprobante = None
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "sub_tipo": "A",
            "responsable": "Cedir",
            "gravado_id": 1,
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante is not None
        assert presentacion.comprobante.fecha_emision == date.today()

    @patch('comprobante.serializers.Afip')
    def test_cerrar_presentacion_con_liquidacion_ok(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.return_value = None
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 2,
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.estado == Presentacion.PENDIENTE
        assert presentacion.comprobante is not None
        assert not afip.emitir_comprobante.called
        assert presentacion.comprobante.fecha_emision == presentacion.fecha

    @patch('comprobante.serializers.Afip')
    def cerrar_presentacion_no_abierta_da_400(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.side_effect = AfipError
        comprobantes_antes = Comprobante.objects.all().count()
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.PENDIENTE
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "sub_tipo": "A",
            "responsable": "Cedir",
            "gravado_id": 1,
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')
        comprobantes_despues = Comprobante.objects.all().count()
        assert response.status_code == 400
        assert comprobantes_antes == comprobantes_despues

    @patch('comprobante.serializers.Afip')
    def test_error_de_afip_no_guarda_comprobante_en_db(self, afip_mock):
        afip = afip_mock()
        afip.emitir_comprobante.side_effect = AfipError
        comprobantes_antes = Comprobante.objects.all().count()
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "sub_tipo": "A",
            "numero": 40,
            "responsable": "Cedir",
            "gravado_id": 1,
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')
        comprobantes_despues = Comprobante.objects.all().count()
        assert response.status_code == 500
        assert comprobantes_antes == comprobantes_despues

    @patch('comprobante.serializers.Afip')
    def test_cerrar_presentacion_total_coincide_con_comprobante(self, afip_mock):
        afip = afip_mock()
        afip.consultar_proximo_numero.return_value = 10
        presentacion = Presentacion.objects.get(pk=1)
        presentacion.estado = Presentacion.ABIERTO
        presentacion.comprobante = None
        presentacion.save()
        datos = {
            "tipo_comprobante_id": 1,
            "sub_tipo": "A",
            "responsable": "Cedir",
            "gravado_id": 1,
        }
        response = self.client.patch('/api/presentacion/1/cerrar/', json.dumps(datos),
                                content_type='application/json')

        assert response.status_code == 200
        presentacion = Presentacion.objects.get(pk=1)
        assert presentacion.total_facturado == presentacion.comprobante.total_facturado