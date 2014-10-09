from django.db import models


class ObraSocial(models.Model):
    id = models.AutoField(primary_key=True, db_column="idObraSocial")
    nombre = models.CharField(db_column="obraSocial", max_length=200)
    #direccion = models.CharField()
    #telefono = models.CharField()
    #localidad = models.CharField()
    #observaciones = models.CharField()

    class Meta:
        db_table = 'cedirData\".\"AlmacenObraSocial'
