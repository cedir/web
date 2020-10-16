from decimal import Decimal
from medico.calculo_honorarios.calculador import CalculadorHonorariosInformeContadora, CalculadorHonorariosPagoMedico
from mock import patch


from django.test import TestCase
from estudio.models import Estudio
from practica.models import Practica
from medico.models import Medico
from medico.calculo_honorarios.descuentos import DescuentoColangios, DescuentoStent, DescuentoPorPolipectomia, DescuentoRadiofrecuencia
from medico.calculo_honorarios.porcentajes import Porcentajes
from medico.calculo_honorarios.constantes import *

COLANGIO_ID = 13
STENT_ID = 48
RADIOFRECUENCIA_ID = 11
POLIPECTOMIA_ID = 18

OSDE = 3
OSDE_CEDIR = 79
OS_UNR = 25
ACA_SALUD = 5
GALENO = 46
OSPAC = 19


class TestDescuentosCalculadorHonorarios(TestCase):
    fixtures = ["medicos.json", "estudios.json", "obras_sociales.json", "practicas.json", "pacientes.json", "presentaciones.json", "comprobantes",
                "anestesistas.json", "medicamentos.json"]

    def test_descuento_por_colangios(self):
        estudios_aplica = Estudio.objects.filter(practica__id=COLANGIO_ID)
        estudios_no_aplica = Estudio.objects.exclude(practica__id=COLANGIO_ID)
        for estudio in estudios_aplica:
            self.assertNotEqual(DescuentoColangios().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_no_aplica:
            self.assertEqual(DescuentoColangios().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_stent(self):
        estudios_aplica = Estudio.objects.filter(practica__id=STENT_ID)
        estudios_no_aplica = Estudio.objects.exclude(practica__id=STENT_ID)
        for estudio in estudios_aplica:
            self.assertNotEqual(DescuentoStent().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_no_aplica:
            self.assertEqual(DescuentoStent().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_radiofrecuencia(self):
        estudios_aplica = Estudio.objects.filter(practica__id=RADIOFRECUENCIA_ID)
        estudios_no_aplica = Estudio.objects.exclude(practica__id=RADIOFRECUENCIA_ID)
        for estudio in estudios_aplica:
            self.assertNotEqual(DescuentoRadiofrecuencia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_no_aplica:
            self.assertEqual(DescuentoRadiofrecuencia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_polipectomia(self):
        estudios_aplica = Estudio.objects.filter(practica__id=POLIPECTOMIA_ID).exclude(obra_social__id__in = [OSDE, OSDE_CEDIR, OS_UNR, ACA_SALUD, GALENO, OSPAC])
        estudios_otra_practica = Estudio.objects.exclude(practica__id=POLIPECTOMIA_ID)
        estudios_obras_sociales_no_aplican = Estudio.objects.filter(practica_id=POLIPECTOMIA_ID, obra_social__id__in = [OSDE, OSDE_CEDIR, OS_UNR, ACA_SALUD, GALENO, OSPAC])
        for estudio in estudios_aplica:
            self.assertNotEqual(DescuentoPorPolipectomia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_otra_practica:
            self.assertEqual(DescuentoPorPolipectomia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_obras_sociales_no_aplican:
            self.assertEqual(DescuentoPorPolipectomia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))


class TestPorcentajesCalculadorHonorarios(TestCase):
    fixtures = ["medicos.json", "estudios.json", "obras_sociales.json", "practicas.json", "pacientes.json", "presentaciones.json", "comprobantes",
                "anestesistas.json", "medicamentos.json"]
    def test_porcentajes_honorarios_medicos_suman_siempre_100(self):
        estudios = Estudio.objects.all()
        for e in estudios:
            p = Porcentajes(e)
            self.assertEqual(p.actuante + p.solicitante + p.cedir, Decimal("100.00"))


    def test_porcentajes_correctos_por_defecto(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(99999)
        estudio.medico = Medico(ID_BRUNETTI[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_POR_DEFECTO_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_POR_DEFECTO_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_POR_DEFECTO_CEDIR)

    def test_porcentajes_correctos_consulta(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_CONSULTA[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_CONSULTA_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_CONSULTA_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_CONSULTA_CEDIR)

    def test_porcentajes_correctos_ecografia(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_ECOGRAFIA[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_ECOGRAFIA_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_ECOGRAFIA_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_ECOGRAFIA_CEDIR)

    def test_porcentajes_correctos_laboratorio(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_LABORATORIO[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_LABORATORIO_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_LABORATORIO_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_LABORATORIO_CEDIR)

    def test_porcentajes_correctos_ligadura(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_LIGADURA[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_LIGADURA_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_LIGADURA_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_LIGADURA_CEDIR)

    def test_porcentajes_correctos_especial(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_ESPECIAL[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_ESPECIAL_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_ESPECIAL_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_ESPECIAL_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_10(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_10[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_ACUERDO_10_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_ACUERDO_10_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_ACUERDO_10_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_40(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_40[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_ACUERDO_40_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_ACUERDO_40_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_ACUERDO_40_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_50(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_50[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_ACUERDO_50_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_ACUERDO_50_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_ACUERDO_50_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_80(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_80[0])
        p = Porcentajes(estudio)
        self.assertEqual(p.actuante, PORCENTAJE_ACUERDO_80_ACTUANTE)
        self.assertEqual(p.solicitante, PORCENTAJE_ACUERDO_80_SOLICITANTE)
        self.assertEqual(p.cedir, PORCENTAJE_ACUERDO_80_CEDIR)

class TestCalculadorHonorarios(TestCase):
    fixtures = ["medicos.json", "estudios.json", "obras_sociales.json", "practicas.json", "pacientes.json", "presentaciones.json", "comprobantes",
                "anestesistas.json", "medicamentos.json"]
    def test_calculador_honorarios_informe_comprobantes(self):
        estudio = Estudio.objects.first()
        calculador = CalculadorHonorariosInformeContadora(estudio)
        self.assertEqual(
            calculador.actuante + calculador.solicitante + calculador.cedir + calculador.uso_de_materiales,
            estudio.importe_estudio - estudio.importe_estudio * calculador.porcentaje_GA() / Decimal(100.0)
        )

    def test_calculador_honorarios_pago_medico_comun(self):
        estudio = Estudio.objects.filter(importe_estudio_cobrado__gt=0).first()
        calculador = CalculadorHonorariosPagoMedico(estudio)
        self.assertEqual(
            calculador.actuante + calculador.solicitante + calculador.cedir + calculador.uso_de_materiales,
            estudio.importe_estudio_cobrado - estudio.importe_estudio_cobrado * calculador.porcentaje_GA() / Decimal(100.0)
        )

    def test_calculador_honorarios_pago_medico_pago_contra_factura(self):
        estudio = Estudio.objects.filter(pago_contra_factura__gt=0).first()
        calculador = CalculadorHonorariosPagoMedico(estudio)
        self.assertEqual(
            calculador.actuante + calculador.solicitante + calculador.cedir + calculador.uso_de_materiales,
            estudio.pago_contra_factura - estudio.pago_contra_factura * calculador.porcentaje_GA() / Decimal(100.0)
        )