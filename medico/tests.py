from decimal import Decimal
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
            self.assertNotEquals(DescuentoColangios().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_no_aplica:
            self.assertEquals(DescuentoColangios().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_stent(self):
        estudios_aplica = Estudio.objects.filter(practica__id=STENT_ID)
        estudios_no_aplica = Estudio.objects.exclude(practica__id=STENT_ID)
        for estudio in estudios_aplica:
            self.assertNotEquals(DescuentoStent().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_no_aplica:
            self.assertEquals(DescuentoStent().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_radiofrecuencia(self):
        estudios_aplica = Estudio.objects.filter(practica__id=RADIOFRECUENCIA_ID)
        estudios_no_aplica = Estudio.objects.exclude(practica__id=RADIOFRECUENCIA_ID)
        for estudio in estudios_aplica:
            self.assertNotEquals(DescuentoRadiofrecuencia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_no_aplica:
            self.assertEquals(DescuentoRadiofrecuencia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_polipectomia(self):
        estudios_aplica = Estudio.objects.filter(practica__id=POLIPECTOMIA_ID).exclude(obra_social__id__in = [OSDE, OSDE_CEDIR, OS_UNR, ACA_SALUD, GALENO, OSPAC])
        estudios_otra_practica = Estudio.objects.exclude(practica__id=POLIPECTOMIA_ID)
        estudios_obras_sociales_no_aplican = Estudio.objects.filter(practica_id=POLIPECTOMIA_ID, obra_social__id__in = [OSDE, OSDE_CEDIR, OS_UNR, ACA_SALUD, GALENO, OSPAC])
        for estudio in estudios_aplica:
            self.assertNotEquals(DescuentoPorPolipectomia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_otra_practica:
            self.assertEquals(DescuentoPorPolipectomia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))
        for estudio in estudios_obras_sociales_no_aplican:
            self.assertEquals(DescuentoPorPolipectomia().aplicar(estudio, Decimal("10000.00")), Decimal("0.00"))


class TestPorcentajesCalculadorHonorarios(TestCase):
    fixtures = ["medicos.json", "estudios.json", "obras_sociales.json", "practicas.json", "pacientes.json", "presentaciones.json", "comprobantes",
                "anestesistas.json", "medicamentos.json"]
    def test_porcentajes_honorarios_medicos_suman_siempre_100(self):
        estudios = Estudio.objects.all()
        for e in estudios:
            p = Porcentajes(e)
            self.assertEquals(p.actuante + p.solicitante + p.cedir, Decimal("100.00"))


    def test_porcentajes_correctos_por_defecto(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(99999)
        estudio.medico = Medico(ID_BRUNETTI[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_POR_DEFECTO_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_POR_DEFECTO_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_POR_DEFECTO_CEDIR)

    def test_porcentajes_correctos_consulta(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_CONSULTA[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_CONSULTA_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_CONSULTA_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_CONSULTA_CEDIR)

    def test_porcentajes_correctos_ecografia(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_ECOGRAFIA[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_ECOGRAFIA_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_ECOGRAFIA_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_ECOGRAFIA_CEDIR)

    def test_porcentajes_correctos_laboratorio(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_LABORATORIO[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_LABORATORIO_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_LABORATORIO_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_LABORATORIO_CEDIR)

    def test_porcentajes_correctos_ligadura(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_LIGADURA[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_LIGADURA_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_LIGADURA_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_LIGADURA_CEDIR)

    def test_porcentajes_correctos_especial(self):
        estudio = Estudio.objects.first()
        estudio.practica = Practica(ID_ESPECIAL[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_ESPECIAL_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_ESPECIAL_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_ESPECIAL_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_10(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_10[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_ACUERDO_10_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_ACUERDO_10_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_ACUERDO_10_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_40(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_40[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_ACUERDO_40_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_ACUERDO_40_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_ACUERDO_40_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_50(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_50[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_ACUERDO_50_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_ACUERDO_50_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_ACUERDO_50_CEDIR)

    def test_porcentajes_correctos_actuante_brunetti_acuerdo_80(self):
        estudio = Estudio.objects.first()
        estudio.medico = Medico(ID_BRUNETTI[0])
        estudio.medico_solicitante = Medico(ID_ACUERDO_80[0])
        p = Porcentajes(estudio)
        self.assertEquals(p.actuante, PORCENTAJE_ACUERDO_80_ACTUANTE)
        self.assertEquals(p.solicitante, PORCENTAJE_ACUERDO_80_SOLICITANTE)
        self.assertEquals(p.cedir, PORCENTAJE_ACUERDO_80_CEDIR)

    