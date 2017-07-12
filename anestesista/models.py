from __future__ import unicode_literals
from datetime import timedelta
from decimal import Decimal

from django.db import models
from comprobante.models import LineaDeComprobante
from paciente.models import Paciente
from obra_social.models import ObraSocial


class Anestesista(models.Model):
    id        = models.AutoField(primary_key=True, db_column="idMedicoAn")
    nombre    = models.CharField("Nombre",max_length=200, db_column="nombreMedicoAn")
    apellido  = models.CharField("Apellido",max_length=200, db_column="apellidoMedicoAn")
    matricula = models.CharField("Matricula",max_length=200, db_column="nroMatricula", null=True, blank=True)
    direccion = models.CharField("Direccion",max_length=200, db_column="direccionMedico", null=True, blank=True)
    localidad = models.CharField("Localidad",max_length=200, db_column="localidadMedico", null=True, blank=True)
    telefono  = models.CharField("Telefono",max_length=200, db_column="telMedico", null=True, blank=True)
    email     = models.EmailField("E-mail",max_length=200, db_column="mail", null=True, blank=True)
    porcentaje_anestesista = models.DecimalField(max_digits=2, decimal_places=2, default='0.00')

    def __unicode__ (self):
        return u'%s, %s' % (self.apellido, self.nombre, )

    class Meta:
        managed = False
        db_table = 'tblMedicosAnestesistas'
        ordering = [u'apellido']


class PagoAnestesistaVM(object):
    pass



class LineaPagoAnestesistaVM(object):
    def get_comprobante_particular(self):
        """
        el comprobante hay que buscarlo usando el DNI del paciente, fechar del comprobante mayor igual a la fecha de estuido y rngo de 30 dias, y buscar palabra anest dentro de la desc del comprobante (factura)
        """
        startdate = self.estudios[0].fecha
        enddate = startdate + timedelta(days=30)
        lineas = LineaDeComprobante.objects.filter(comprobante__nro_cuit=self.paciente.dni, comprobante__fecha_emision__range=[startdate, enddate], concepto__icontains='anest')
        if bool(lineas):
            return lineas[0].comprobante

    def get_comprobante_desde_facturacion(self):
        """
        # Si no va por ara y es de obra social (no particular) se saca el iva del comprobante asociado a la presentacion.
        """
        estudio = self.estudios[0]
        if estudio.presentacion_id:  # esto puede ser = 0 si no esta facturado
            return estudio.presentacion.comprobante

    def get_coeficiente_paciente_diferenciado(self):
        """
        Si la edad del paciente esta entre 1 a 12 o mayor a 70, se considera diferenciado.
        En este caso, el coficiente es 1.3 (30% mas). De otro modo es 1 (100%)
        """
        if self.es_paciente_diferenciado:
            return Decimal('1.3')
        return Decimal('1')


class ComplejidadEstudio(models.Model):
    estudios = models.CharField(max_length=500, blank=True, null=True)
    formula = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblComplejidadEstudios'


class Complejidad(models.Model):
    importe = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblComplejidades'


#class PagoAnestesista(models.Model):
#    anestesista = models.ForeignKey(Anestesista)
#    anio = models.IntegerField()
#    mes = models.IntegerField()
#    creado = models.DateTimeField(auto_now_add=True)
#    modificado = models.DateTimeField(auto_now=True)

#class LineaPagoAnestesista(models.Model):
#    pago = models.ForeignKey(PagoAnestesista, related_name="lineas")
#    paciente = models.ForeignKey(Paciente)
#    obra_social = models.ForeignKey(ObraSocial)
#    estudios = models.ManyToManyField('estudio.Estudio')
#    es_paciente_diferenciado = models.BooleanField()
#    formula = models.CharField(max_length=200)
#    formula_valorizada = models.CharField(max_length=500)
#    importe = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')
#    alicuota_iva = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')
#    porcentaje_anestesista = models.DecimalField(max_digits=2, decimal_places=2, default='0.00')





