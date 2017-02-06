from __future__ import unicode_literals

from django.db import models
from paciente.models import Paciente
from obra_social.models import ObraSocial

class PagoAnestesistaVM:
    pass

class LineaPagoAnestesistaVM:
    pass

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

# Create your models here.
class Anestesista(models.Model):
    id        = models.AutoField(primary_key=True, db_column="idMedicoAn")
    nombre    = models.CharField("Nombre",max_length=200, db_column="nombreMedicoAn")
    apellido  = models.CharField("Apellido",max_length=200, db_column="apellidoMedicoAn")
    matricula = models.CharField("Matricula",max_length=200, db_column="nroMatricula", null=True, blank=True)
    direccion = models.CharField("Direccion",max_length=200, db_column="direccionMedico", null=True, blank=True)
    localidad = models.CharField("Localidad",max_length=200, db_column="localidadMedico", null=True, blank=True)
    telefono  = models.CharField("Telefono",max_length=200, db_column="telMedico", null=True, blank=True)
    email     = models.EmailField("E-mail",max_length=200, db_column="mail", null=True, blank=True)

    def __unicode__ (self):
        return u'%s, %s' % (self.apellido, self.nombre, )

    class Meta:
        managed = False
        db_table = 'tblMedicosAnestesistas'
        ordering = [u'apellido']


class PagoAnestesista(models.Model):
    anestesista = models.ForeignKey(Anestesista)
    anio = models.IntegerField()
    mes = models.IntegerField()
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

class LineaPagoAnestesista(models.Model):
    pago = models.ForeignKey(PagoAnestesista, related_name="lineas")
    paciente = models.ForeignKey(Paciente)
    obra_social = models.ForeignKey(ObraSocial)
    estudios = models.ManyToManyField('estudio.Estudio')
    es_paciente_diferenciado = models.BooleanField()
    formula = models.CharField(max_length=200)
    formula_valorizada = models.CharField(max_length=500)
    importe = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')
    alicuota_iva = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')
