from decimal import Decimal
from django.test import TestCase
from estudio.models import Estudio
from medico.calculo_honorarios.descuentos import DescuentoColangios, DescuentoStent, DescuentoPorPolipectomia, DescuentoRadiofrecuencia


class TestDescuentosCalculadorHonorarios(TestCase):
    fixtures = ["medicos.json", "estudios.json", "obras_sociales.json", "practicas.json", "pacientes.json", "presentaciones.json", "comprobantes",
                "anestesistas.json"]

    def test_descuento_por_colangios(self):
        estudio_aplica = Estudio.objects.get(pk=3)
        estudio_no_aplica = Estudio.objects.get(pk=4)
        self.assertNotEquals(DescuentoColangios().aplicar(estudio_aplica, Decimal("10000.00")), Decimal("0.00"))
        self.assertEquals(DescuentoColangios().aplicar(estudio_no_aplica, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_stent(self):
        estudio_aplica = Estudio.objects.get(pk=4)
        estudio_no_aplica = Estudio.objects.get(pk=3)
        self.assertNotEquals(DescuentoStent().aplicar(estudio_aplica, Decimal("10000.00")), Decimal("0.00"))
        self.assertEquals(DescuentoColangios().aplicar(estudio_no_aplica, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_radiofrecuencia(self):
        estudio_aplica = Estudio.objects.get(pk=5)
        estudio_no_aplica = Estudio.objects.get(pk=3)
        self.assertNotEquals(DescuentoRadiofrecuencia().aplicar(estudio_aplica, Decimal("10000.00")), Decimal("0.00"))
        self.assertEquals(DescuentoRadiofrecuencia().aplicar(estudio_no_aplica, Decimal("10000.00")), Decimal("0.00"))

    def test_descuentos_por_polipectomia(self):
        estudio_aplica = Estudio.objects.get(pk=6)
        estudios_no_aplican = Estudio.objects.filter(pk__in=[3, 7, 8])
        self.assertNotEquals(DescuentoPorPolipectomia().aplicar(estudio_aplica, Decimal("10000.00")), Decimal("0.00"))
        for est in estudios_no_aplican:
            self.assertEquals(DescuentoPorPolipectomia().aplicar(est, Decimal("10000.00")), Decimal("0.00"))
