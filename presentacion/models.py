from decimal import Decimal

from django.db import models
from comprobante.models import Comprobante
from obra_social.models import ObraSocial


class Presentacion(models.Model):

    PENDIENTE = 0
    COBRADO = 1
    ABIERTO = 2

    ESTADOS = (
        (PENDIENTE, 'Pendiente'),  # 'estado = 0 significa que esta facturado, y no se pueden agregar mas estudios ni modificar nada porque esta cerrado
        (COBRADO, 'Cobrado'),    # 'estado = 1 significa que se facturo y se cobro
        (ABIERTO, 'Abierto'),    # 'estado = 2 la facturacion esta abierta a agregar o modificar estudios
    )

    id = models.AutoField(primary_key=True, db_column=u'idFacturacion')
    obra_social = models.ForeignKey(ObraSocial, db_column=u'idObraSocial')
    comprobante = models.ForeignKey(Comprobante, db_column=u'idComprobante', related_name=u'presentacion')
    fecha = models.DateField(u'Fecha', db_column=u'fechaFacturacion')
    estado = models.SmallIntegerField(db_column=u'pagado', choices=ESTADOS)
    periodo = models.CharField(max_length=128)
    iva = models.DecimalField(max_digits=16, decimal_places=2)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    total_facturado = models.DecimalField(db_column=u'totalFacturado', max_digits=16, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'tblFacturacion'

    def __unicode__(self):
        return u'%s %s' % (self.fecha, self.obra_social)


class PagoPresentacion(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'idPagoFact')
    presentacion = models.ForeignKey(Presentacion, db_column=u'idFacturacion', related_name=u'pago')
    fecha = models.DateField(u'Fecha', db_column=u'fechaPagoFact')
    nro_recivo = models.CharField(max_length=128, db_column=u'nroRecivo')
    importe = models.DecimalField(db_column=u'importePago', max_digits=16, decimal_places=2)
    gasto_administrativo = models.DecimalField(db_column=u'gastoAdministrativo', default=Decimal('0.00'), max_digits=16, decimal_places=2)

    class Meta:
        db_table = 'tblPagoFacturacion'
