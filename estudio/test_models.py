from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from estudio.models import Estudio


class PagoContraFacturaTest(TestCase):
    fixtures = ['comprobantes.json', 'pacientes.json', 'medicos.json', "anestesistas.json", 'practicas.json',
                'obras_sociales.json', 'presentaciones.json', 'estudios.json', "medicamentos.json"]

    def setUp(self):
        self.estudio = Estudio.objects.get(pk=1)
        self.nuevo_importe_pago_contra_factura = Decimal(3322)

    def test_set_pago_contra_factura_success(self):
        self.estudio.presentacion = None
        self.estudio.fecha_cobro = None

        self.assertFalse(bool(self.estudio.es_pago_contra_factura))
        self.assertEqual(self.estudio.pago_contra_factura, Decimal(0))

        self.estudio.set_pago_contra_factura(self.nuevo_importe_pago_contra_factura)

        self.assertTrue(bool(self.estudio.es_pago_contra_factura))
        self.assertEqual(self.estudio.pago_contra_factura, self.nuevo_importe_pago_contra_factura)
        self.assertEqual(self.estudio.fecha_cobro.date(), datetime.today().date())

    def test_set_pago_contra_factura_a_estudio_que_ya_esta_como_pago_contra_factura(self):
        self.estudio.es_pago_contra_factura = 1
        self.estudio.fecha_cobro = datetime.today() - timedelta(days=1)
        self.estudio.presentacion = None
        self.estudio.pago_contra_factura = 22
        self.estudio.save()

        self.estudio.set_pago_contra_factura(self.nuevo_importe_pago_contra_factura)

        self.assertTrue(bool(self.estudio.es_pago_contra_factura))
        self.assertEqual(self.estudio.pago_contra_factura, self.nuevo_importe_pago_contra_factura)
        self.assertEqual(self.estudio.fecha_cobro.date(), datetime.today().date())

    def test_set_pago_contra_factura_devuelve_error_si_el_estudio_esta_presentado(self):
        self.assertTrue(self.estudio.presentacion)
        self.estudio.fecha_cobro = None

        with self.assertRaises(AssertionError) as context:
            self.estudio.set_pago_contra_factura(self.nuevo_importe_pago_contra_factura)
            self.assertTrue(u'Estudio ya fue presentado y no puede modificarse' in context.exception)

    def test_set_pago_contra_factura_devuelve_error_si_el_estudio_esta_pagado_al_actuante(self):
        self.estudio.pago_medico_actuante_id = 1
        self.estudio.pago_medico_solicitante = None
        self.estudio.presentacion = None

        with self.assertRaises(AssertionError) as context:
            self.estudio.set_pago_contra_factura(self.nuevo_importe_pago_contra_factura)
            self.assertTrue(u'Estudio ya fue pagado al medico y no puede modificarse' in context.exception)

    def test_set_pago_contra_factura_devuelve_error_si_el_estudio_esta_pagado_al_solicitante(self):
        self.estudio.pago_medico_solicitante_id = 1
        self.estudio.pago_medico_actuante = None
        self.estudio.presentacion = None

        with self.assertRaises(AssertionError) as context:
            self.estudio.set_pago_contra_factura(self.nuevo_importe_pago_contra_factura)
            self.assertTrue(u'Estudio ya fue pagado al medico y no puede modificarse' in context.exception)

    def test_anular_pago_contra_factura_success(self):
        self.estudio.es_pago_contra_factura = 1
        self.estudio.fecha_cobro = datetime.today() - timedelta(days=1)
        self.estudio.presentacion = None
        self.estudio.pago_contra_factura = 22
        self.estudio.save()

        self.estudio.anular_pago_contra_factura()

        self.assertFalse(bool(self.estudio.es_pago_contra_factura))
        self.assertEqual(self.estudio.pago_contra_factura, Decimal(0))
        self.assertEqual(self.estudio.fecha_cobro, None)

    def test_anular_pago_contra_factura_devuelve_error_si_el_estudio_no_es_pago_contra_factura(self):
        self.estudio.es_pago_contra_factura = 0
        self.estudio.fecha_cobro = datetime.today() - timedelta(days=1)
        self.estudio.presentacion = None
        self.estudio.pago_contra_factura = Decimal(0)
        self.estudio.save()

        with self.assertRaises(AssertionError) as context:
            self.estudio.anular_pago_contra_factura()
            self.assertTrue(u'El estudio no esta como Pago Contra Factura' in context.exception)
            self.assertFalse(bool(self.estudio.es_pago_contra_factura))
            self.assertEqual(self.estudio.pago_contra_factura, Decimal(0))
            self.assertEqual(self.estudio.fecha_cobro, None)

    def test_anular_pago_contra_factura_devuelve_error_si_el_estudio_fue_ya_pagado_al_actuante(self):
        self.estudio.pago_medico_actuante_id = 1
        self.estudio.pago_medico_solicitante = None
        self.estudio.es_pago_contra_factura = 1
        self.estudio.fecha_cobro = datetime.today() - timedelta(days=1)
        self.estudio.presentacion = None
        self.estudio.pago_contra_factura = 22

        with self.assertRaises(AssertionError) as context:
            self.estudio.anular_pago_contra_factura()
            self.assertTrue(u'Estudio ya fue pagado al medico y no puede modificarse' in context.exception)

    def test_anular_pago_contra_factura_devuelve_error_si_el_estudio_fue_ya_pagado_al_solicitante(self):
        self.estudio.pago_medico_actuante = None
        self.estudio.pago_medico_solicitante_id = 1
        self.estudio.es_pago_contra_factura = 1
        self.estudio.fecha_cobro = datetime.today() - timedelta(days=1)
        self.estudio.presentacion = None
        self.estudio.pago_contra_factura = 22

        with self.assertRaises(AssertionError) as context:
            self.estudio.anular_pago_contra_factura()
            self.assertTrue(u'Estudio ya fue pagado al medico y no puede modificarse' in context.exception)
