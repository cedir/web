from django.db import models


class Practica(models.Model):
    id = models.AutoField(primary_key=True, db_column="idEstudio")
    descripcion = models.CharField("Descripcion",max_length=200, db_column="estudio")
    codigoMedico = models.CharField(max_length=50, blank=True)
    codigo_medico_osde = models.CharField(max_length=50, db_column="codigoMedicoOSDE", blank=True)
    abreviatura = models.CharField(max_length=20, blank=True)
    usedLevel = models.IntegerField(default=0)
    porcentaje_medico = models.IntegerField(db_column="porcentajeMedico", default=0)

    class Meta:
        db_table = 'AlmacenEstudios'
        ordering = ['descripcion']

    def __str__(self):
        return '%s' % (self.abreviatura or self.descripcion)
