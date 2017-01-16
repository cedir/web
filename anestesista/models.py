from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Anestesista(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicoAn")
    nombre = models.CharField("Nombre",max_length=200, db_column="nombreMedicoAn")
    apellido = models.CharField("Apellido",max_length=200, db_column="apellidoMedicoAn")
    matricula = models.CharField("Matricula",max_length=200, db_column="nroMatricula", null=True, blank=True)
    direccion = models.CharField("Direccion",max_length=200, db_column="direccionMedico", null=True, blank=True)
    localidad = models.CharField("Localidad",max_length=200, db_column="localidadMedico", null=True, blank=True)
    telefono = models.CharField("Telefono",max_length=200, db_column="telMedico", null=True, blank=True)
    email = models.EmailField("E-mail",max_length=200, db_column="mail", null=True, blank=True)

    def __unicode__ (self):
        return u'%s, %s' % (self.apellido, self.nombre, )

    class Meta:
        db_table = 'tblMedicosAnestesistas'
        ordering = [u'apellido']