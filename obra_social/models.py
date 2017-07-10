from django.db import models


class ObraSocial(models.Model):
    id = models.AutoField(primary_key=True, db_column="idObraSocial")
    nombre = models.CharField(db_column="obraSocial", max_length=200)
    se_presenta_por_ARA = models.BooleanField(db_column='sePresentaPorARA', default=0)
    #direccion = models.CharField()
    #telefono = models.CharField()
    #localidad = models.CharField()
    #observaciones = models.CharField()

    class Meta:
        db_table = 'AlmacenObraSocial'
        ordering = ['nombre']

    def __unicode__(self):
        return u'%s' % self.nombre

    def is_particular_or_especial(self):
        return self.nombre in ('PARTICULAR', 'PARTICULAR ESPECIAL', )

