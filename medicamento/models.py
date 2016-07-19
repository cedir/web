# -*- coding: utf-8
from django.db import models

class Medicamento(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicamento")
    descripcion = models.CharField(db_column="descripcionMedicamento", max_length=300, blank=True)

    importe = models.DecimalField(db_column="importeMedicamento", max_digits=16, decimal_places=2, default='0.00')
    stock = models.PositiveSmallIntegerField(max_length=16, )


  #tipo character varying(20) DEFAULT 'Medicación'::character varying,
  #"codigoMedicoOSDE" character varying DEFAULT ''::character varying,

    class Meta:
        db_table = 'tblMedicamentos'
