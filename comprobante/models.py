from django.db import models
from datetime import timedelta

class TipoComprobante(models.Model):
    nombre = models.CharField(max_length=128, db_column=u'tipoComprobante')

    class Meta:
        db_table = 'cedirData\".\"tblComprobantesTipo'


class Gravado(models.Model):
    descripcion = models.CharField(max_length=128, db_column=u'descripcionGravado')
    porcentaje = models.FloatField(db_column=u'porcentajeGravado')

    class Meta:
        db_table = 'cedirData\".\"tblGravado'


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
    nro_terminal = models.SmallIntegerField(db_column=u'nroTerminal', default=1)
    cae = models.CharField(max_length=128, db_column=u'CAE')
    total_facturado = models.FloatField(db_column=u'totalFacturado', default=0)
    total_cobrado = models.FloatField(db_column=u'totalCobrado')
    fecha_emision = models.DateField(db_column=u'fechaEmision')
    fecha_recepcion = models.DateField(db_column=u'fechaRecepcion')

    tipo_comprobante = models.ForeignKey(TipoComprobante, db_column=u'idTipoComprobante')
    factura = models.ForeignKey(u'comprobante.Comprobante', db_column=u'idFactura', null=True, blank=True)
    gravado = models.ForeignKey(Gravado, db_column=u'gravado', null=True, blank=True)

    cae = models.TextField(db_column='CAE', blank=True)
    vencimiento_cae = models.DateField(db_column='vencimientoCAE', blank=True, null=True)

    @property
    def codigo_afip(self):
        conversion = {
            'A': {1: 1, 3: 2, 4: 3},
            'B': {1: 6, 3: 7, 4: 8}
        }
        return conversion[self.sub_tipo][self.tipo_comprobante.id]

    @property
    def tipo_id_afip(self):
        return 80 if len(self.nro_cuit.replace('-', '')) > 10 else 96

    @property
    def nro_id_afip(self):
        return self.nro_cuit.replace('-', '')

    @property
    def importe_excento_afip(self):
        return 0 if self.gravado and self.gravado.porcentaje else self.total_facturado

    @property
    def importe_gravado_afip(self):
        return (self.total_facturado * 100) / (100 + self.gravado.porcentaje) if self.gravado and self.gravado.porcentaje else 0

    @property
    def importe_alicuota_afip(self):
        return (self.total_facturado * self.gravado.porcentaje) / (100 + self.gravado.porcentaje) if self.gravado and self.gravado.porcentaje else 0

    @property
    def codigo_operacion_afip(self):
        return '0' if self.gravado and self.gravado.porcentaje else 'E'

    @property
    def codigo_alicuota_afip(self):
        return (2 + self.gravado.id) if self.gravado else 3

    @property
    def fecha_vencimiento(self):
        return self.fecha_emision + timedelta(days=30)

    class Meta:
        managed = False
        db_table = 'cedirData\".\"tblComprobantes'

class LineaDeComprobante(models.Model):
    comprobante = models.ForeignKey(Comprobante, db_column=u'idComprobante', related_name=u'lineas')
    concepto = models.CharField(max_length=128, )
    sub_total = models.FloatField(db_column=u'subtotal', )
    iva = models.FloatField(db_column=u'importeIVA', )
    importe_neto = models.FloatField(db_column=u'importeNeto', )

    class Meta:
        db_table = 'cedirData\".\"tblComprobanteLineas'
