from decimal import Decimal
from django.test import TestCase
from estudio.models import Estudio
from medico.calculo_honorarios.descuentos import DescuentoColangios, DescuentoStent, DescuentoPorPolipectomia, DescuentoRadiofrecuencia

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
                "anestesistas.json"]

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
