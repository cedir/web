from django.db import models
from medico.models import Medico
from estudio.models import Estudio


class TipoMovimientoCaja(models.Model):
    descripcion = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'tblCajaTipoDeMovimientos'


class MovimientoCaja(models.Model):
    concepto = models.TextField(blank=True)
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField()
    tipo = models.ForeignKey(TipoMovimientoCaja, db_column='idTipoDeMovimiento', blank=True, null=True)
    estudio = models.ForeignKey(Estudio, db_column='nroEstudio', related_name='movimientos_caja', blank=True, null=True)
    medico = models.ForeignKey(Medico, db_column='idMedico', blank=True, null=True)
    monto = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    monto_acumulado = models.DecimalField(db_column='montoAcumulado', max_digits=14, decimal_places=2, blank=True, null=True)
    estado = models.NullBooleanField()

    class Meta:
        db_table = 'tblCajaMovimientos'
