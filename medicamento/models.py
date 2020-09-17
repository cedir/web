# -*- coding: utf-8
from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save

from medico.models import Medico

TIPOS_MEDICAMENTOS = (
    ('Mat Esp', 'Material Especifico'),
    ('Medicación', 'Medicación'),
)


class Medicamento(models.Model):
    id = models.AutoField(primary_key=True, db_column='idMedicamento')
    descripcion = models.CharField(db_column='descripcionMedicamento', max_length=300, blank=True)
    importe = models.DecimalField(db_column='importeMedicamento', max_digits=16, decimal_places=2, default=Decimal('0.00'))
    stock = models.PositiveSmallIntegerField(default=0)
    tipo = models.CharField(max_length=100, default='Medicación', choices=TIPOS_MEDICAMENTOS)
    codigo_osde = models.CharField(max_length=100, db_column='codigoMedicoOSDE', blank=True, default='')

    class Meta:
        db_table = 'tblMedicamentos'

    def __unicode__(self):
        return '%s (%s)' % (self.descripcion, self.tipo)


class Movimiento(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    cantidad = models.IntegerField()
    descripcion = models.CharField(max_length=300)
    medicamento = models.ForeignKey(Medicamento, db_column='idMedicamento')

    class Meta:
        db_table = 'tblMovimientosDeMedicamentos'

    def has_delete_permission(self, request, obj=None):
        return False

    @property
    def tipo(self):
        if not self.id:
            return '-'  # creating mode

        if self.cantidad > 0:
            return 'Ingreso'
        if self.cantidad < 0:
            return 'Egreso'
        return '-'

    def save(self, *args, **kwargs):
        """ Disable update"""
        if self.id:
            return
        super(Movimiento, self).save(*args, **kwargs)


def update_stock_medicamento(sender, instance, **kwargs):
    medicamento = Medicamento.objects.get(pk=instance.medicamento.id)  # refresh data
    medicamento.stock += instance.cantidad
    medicamento.save()

post_save.connect(update_stock_medicamento, sender=Movimiento, dispatch_uid="update_stock_medicamentos")

