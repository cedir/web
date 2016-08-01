# -*- coding: utf-8
from django.db import models
from medico.models import Medico

TIPOS_MEDICAMENTOS = (
    ('Mat Esp', 'Material Especifico'),
    ('Medicación', 'Medicación'),
)


class Medicamento(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'idMedicamento')
    descripcion = models.CharField(db_column=u'descripcionMedicamento', max_length=300, blank=True)
    importe = models.DecimalField(db_column=u'importeMedicamento', max_digits=16, decimal_places=2, default='0.00')
    stock = models.PositiveSmallIntegerField(max_length=16, )
    tipo = models.CharField(max_length=100, default=u'Medicación', choices=TIPOS_MEDICAMENTOS)
    codigo_osde = models.CharField(max_length=100, db_column=u'codigoMedicoOSDE', blank=True, default=u'')

    class Meta:
        db_table = 'tblMedicamentos'

    def __unicode__(self):
        return u'%s (%s)' % (self.descripcion, self.tipo)


class Movimiento(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    cantidad = models.IntegerField(max_length=10, )
    descripcion = models.CharField(max_length=300)
    medicamento = models.ForeignKey(Medicamento, db_column=u'idMedicamento')

    class Meta:
        db_table = 'tblMovimientosDeMedicamentos'

    def has_delete_permission(self, request, obj=None):
        return False

    def save(self, *args, **kwargs):
        """ Disable update"""
        if self.id:
            return
        super(Movimiento, self).save(*args, **kwargs)

        # actualizar stock en medicamento
        medicamento = Medicamento.objects.get(pk=self.medicamento.id)  # refresh data
        medicamento.stock += self.cantidad
        medicamento.save()

# TODO: ver si se peude hacer esto con el post-save de signals
# TODO: ver por que aparece None en el listado de medicamentos para el campo tipo solo cuando es medicamento
