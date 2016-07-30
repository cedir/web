from django.db import models


class Practica(models.Model):
    id = models.AutoField(primary_key=True, db_column="idEstudio")
    descripcion = models.CharField("Descripcion",max_length=200, db_column="estudio")
    codigoMedico = models.CharField(max_length=50)
    abreviatura = models.CharField(max_length=20)
    usedLevel = models.IntegerField()
    #duracion = models.CharField("Duracion",max_length=200, null=False,blank=False)

    def mostrar(self):
        return u'%s' % (self.abreviatura or self.descripcion)

    class Meta:
        db_table = u'AlmacenEstudios'
        ordering = ['descripcion']

    def __unicode__(self):
        return u'%s' % self.descripcion
