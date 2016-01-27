from django.db import models


class Gravado(models.Model):
    descripcion = models.CharField(max_length=128, db_column=u'descripcionGravado')
    porcentaje = models.FloatField(db_column=u'porcentajeGravado')

    class Meta:
        db_table = 'cedirData\".\"tblGravado'


class TipoComprobante(models.Model):
    nombre = models.CharField(max_length=128, db_column=u'tipoComprobante')

    class Meta:
        db_table = 'cedirData\".\"tblComprobantesTipo'


class Comprobante(models.Model):
    nombre_cliente = models.CharField(max_length=128, db_column=u'nombreCliente')
    domicilio_cliente = models.CharField(max_length=128, db_column=u'domicilioCliente')
    nro_cuit = models.CharField(max_length=128, db_column=u'nroCuit')
    gravado_paciente = models.CharField(max_length=128, db_column=u'gravadoPaciente')
    condicion_fiscal = models.CharField(max_length=128, db_column=u'condicionFiscal')
    responsable = models.CharField(max_length=128, )
    sub_tipo = models.CharField(max_length=50, db_column=u'subTipo')
    estado = models.CharField(max_length=50, )
    numero = models.IntegerField(db_column=u'nroComprobante', )
    nroTerminal = models.SmallIntegerField(db_column=u'fechaRecepcion', default=1)
    cae = models.CharField(max_length=128, db_column=u'CAE')
    total_facturado = models.FloatField(db_column=u'totalFacturado', default=0)
    total_cobrado = models.FloatField(db_column=u'totalCobrado')
    fecha_emision = models.DateField(db_column=u'fechaEmision')
    fecha_recepcion = models.DateField(db_column=u'fechaRecepcion')

    tipo_comprobante = models.ForeignKey(TipoComprobante, db_column=u'idTipoComprobante')
    factura = models.ForeignKey(u'comprobante.Comprobante', db_column=u'idFactura', null=True, blank=True)
    gravado = models.ForeignKey(Gravado, db_column=u'gravado', null=True, blank=True)


    class Meta:
        db_table = 'cedirData\".\"tblComprobantes'

class LineaDeComprobante(models.Model):
    comprobante = models.ForeignKey(Comprobante, db_column=u'idComprobante', related_name=u'lineas')
    concepto = models.CharField(max_length=128, )
    sub_total = models.FloatField(db_column=u'subtotal', )
    iva = models.FloatField(db_column=u'importeIVA', )
    importe_neto = models.FloatField(db_column=u'importeNeto', )

    class Meta:
        db_table = 'cedirData\".\"tblComprobanteLineas'


