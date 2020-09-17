# -*- coding: utf-8 -*-
from django.db import models

CONDICIONES_FISCALES = (('CONSUMIDOR FINAL', 'CONSUMIDOR FINAL'),
                        ('RESPONSABLE INSCRIPTO', 'RESPONSABLE INSCRIPTO'),
                        ('EXENTO', 'EXENTO'))
BOOLEANOS = (('1', 'Si'),
             ('0', 'No'))


class ObraSocial(models.Model):
    id = models.AutoField(primary_key=True, db_column="idObraSocial")
    nombre = models.CharField(db_column="obraSocial", max_length=200)

    # Estos fields estan representados como chars con choice porque en la DB son SmallInt
    se_presenta_por_ARA = models.CharField('Se presenta por ARA', db_column='sePresentaPorARA', max_length=200,
                                           choices=BOOLEANOS, default=0)
    se_presenta_por_AMR = models.CharField('Se presenta por AMR', db_column='sePresentaPorAMR', max_length=200,
                                           choices=BOOLEANOS, default=0)
    direccion = models.CharField("Dirección", db_column='direccion', max_length=200,
                                 blank=True, default='')
    telefono = models.CharField('Teléfono', db_column='telefono', max_length=200,
                                blank=True, default='')
    localidad = models.CharField('Localidad', db_column='localidad', max_length=200,
                                 blank=True, default='')
    codigo_postal = models.IntegerField(
        'Código Postal', db_column='codigoPostal', blank=True, default=0)
    condicion_fiscal = models.CharField('Condición Fiscal', db_column='condicionFiscal', max_length=200,
                                        choices=CONDICIONES_FISCALES, default='CONSUMIDOR FINAL')
    observaciones = models.TextField(
        'Observaciones', db_column="observaciones", blank=True)
    valor_aproximado_pension = models.DecimalField(
        'Valor Aproximado Pension', db_column='valorAproximadoPension', max_digits=10, decimal_places=2, default=0)

    nro_cuit = models.CharField('CUIT', db_column='nroCuit', max_length=200, default="")

    class Meta(object):
        db_table = 'AlmacenObraSocial'
        ordering = ['nombre']

    def __unicode__(self):
        return '%s' % self.nombre

    def is_particular_or_especial(self):
        return self.nombre in ('PARTICULAR', 'PARTICULAR ESPECIAL', )


class ArancelObraSocial(models.Model):
    practica = models.ForeignKey('practica.Practica', db_column='idEstudio')
    obra_social = models.ForeignKey(ObraSocial, db_column='idObraSocial', )
    precio = models.DecimalField(
        db_column='Precio', max_digits=16, decimal_places=2)
    precio_anestesia = models.DecimalField(
        db_column='precioAnestesia', max_digits=16, decimal_places=2)
    fecha = models.DateField()

    class Meta(object):
        unique_together = (("practica", "obra_social"),)
        db_table = 'AlmacenPreciosEstOS'
