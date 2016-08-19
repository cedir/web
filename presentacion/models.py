from django.db import models
from comprobante.models import Comprobante
from obra_social.models import ObraSocial

PENDIENTE = 0
COBRADO = 1
ABIERTO = 2

ESTADOS = (
    (PENDIENTE, 'Pendiente'),  # 'estado = 0 significa que esta facturado, y no se pueden agregar mas estudios ni modificar nada porque esta cerrado
    (COBRADO, 'Cobrado'),    # 'estado = 1 significa que se facturo y se cobro
    (ABIERTO, 'Abierto'),    # 'estado = 2 la facturacion esta abierta a agregar o modificar estudios
)


class Presentacion(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'idFacturacion')
    obra_social = models.ForeignKey(ObraSocial, db_column=u'idObraSocial')
    comprobante = models.ForeignKey(Comprobante, db_column=u'idComprobante')
    fecha = models.DateField(u'Fecha', db_column=u'fechaFacturacion')
    estado = models.SmallIntegerField(db_column=u'pagado', choices=ESTADOS)
    periodo = models.CharField(max_length=128)
    iva = models.FloatField()
    total = models.FloatField(default='0')
    totalFacturado = models.FloatField(default='0')

    #"tipoFactura" smallint, no me acuerdo para que se usa esto
    #"responsableDeFactura" character varying, no me acuerdo para que se usa esto


    class Meta:
        db_table = 'tblFacturacion'

    def __unicode__(self):
        return u'%s %s' % (self.fecha, self.obra_social)


class PagoPresentacion(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'idPagoFact')
    presentacion = models.ForeignKey(Presentacion, db_column=u'idFacturacion', related_name=u'pago')
    fecha = models.DateField(u'Fecha', db_column=u'fechaPagoFact')
    nro_recivo = models.CharField(max_length=128, db_column=u'nroRecivo')
    importe = models.FloatField(db_column=u'importePago')
    gasto_administrativo = models.FloatField(db_column=u'gastoAdministrativo', default='0')
    
    class Meta:
        db_table = 'tblPagoFacturacion'
