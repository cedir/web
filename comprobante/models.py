from datetime import timedelta
from django.db import models

ID_TIPO_COMPROBANTE_FACTURA = 1
ID_TIPO_COMPROBANTE_LIQUIDACION = 2
ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO = 3
ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO = 4
ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA = 5
ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA = 6
ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA = 7

class TipoComprobante(models.Model):
    nombre = models.CharField(max_length=128, db_column=u'tipoComprobante')

    class Meta:
        db_table = 'tblComprobantesTipo'

    def __unicode__(self):
        return self.nombre


class Gravado(models.Model):
    descripcion = models.CharField(max_length=128, db_column=u'descripcionGravado')
    porcentaje = models.DecimalField(db_column=u'porcentajeGravado', max_digits=4, decimal_places=2)

    class Meta(object):
        db_table = 'tblGravado'


class Comprobante(models.Model):

    ANULADO = u'ANULADO'
    NO_COBRADO = u'NO COBRADO'
    COBRADO = u'COBRADO'

    ESTADOS = (
        (ANULADO, ANULADO),
        (NO_COBRADO, NO_COBRADO),
        (COBRADO, COBRADO),
    )

    nombre_cliente = models.CharField(max_length=128, db_column=u'nombreCliente')
    domicilio_cliente = models.CharField(max_length=128, db_column=u'domicilioCliente')
    nro_cuit = models.CharField(max_length=128, db_column=u'nroCuit')
    gravado_paciente = models.CharField(max_length=128, db_column=u'gravadoPaciente')
    condicion_fiscal = models.CharField(max_length=128, db_column=u'condicionFiscal')
    responsable = models.CharField(max_length=128, )
    sub_tipo = models.CharField(max_length=50, db_column=u'subTipo')
    estado = models.CharField(max_length=50, choices=ESTADOS)
    numero = models.IntegerField(db_column=u'nroComprobante', )
    nro_terminal = models.SmallIntegerField(db_column=u'nroTerminal', default=1)
    total_facturado = models.DecimalField(db_column=u'totalFacturado', max_digits=16, decimal_places=2, default=0)
    total_cobrado = models.DecimalField(db_column=u'totalCobrado', max_digits=16, decimal_places=2)
    fecha_emision = models.DateField(db_column=u'fechaEmision')
    fecha_recepcion = models.DateField(db_column=u'fechaRecepcion')

    tipo_comprobante = models.ForeignKey(TipoComprobante, db_column=u'idTipoComprobante')
    factura = models.ForeignKey(u'comprobante.Comprobante', db_column=u'idFactura', null=True, blank=True)
    gravado = models.ForeignKey(Gravado, db_column=u'gravado', null=True, blank=True)

    cae = models.CharField(max_length=128, db_column=u'CAE', null=True, blank=True)
    vencimiento_cae = models.DateField(db_column='vencimientoCAE', blank=True, null=True)

    @property
    def codigo_afip(self):
        conversion = {
            'A': {
                ID_TIPO_COMPROBANTE_FACTURA: 1,
                ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO: 2,
                ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO: 3,
                ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA: 201,
                ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA: 202,
                ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA: 203
            },
            'B': {
                ID_TIPO_COMPROBANTE_FACTURA: 6,
                ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO: 7,
                ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO: 8,
                ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA: 206,
                ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA: 207,
                ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA: 208
            }
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

    class Meta(object):
        permissions = (
            ("informe_ventas", u"Permite generar el informe de ventas."),
        )
        db_table = 'tblComprobantes'


class LineaDeComprobante(models.Model):
    comprobante = models.ForeignKey(Comprobante, db_column=u'idComprobante', related_name=u'lineas')
    concepto = models.CharField(max_length=128, )
    sub_total = models.DecimalField(db_column=u'subtotal', max_digits=16, decimal_places=2)
    iva = models.DecimalField(db_column=u'importeIVA', max_digits=16, decimal_places=2)
    importe_neto = models.DecimalField(db_column=u'importeNeto', max_digits=16, decimal_places=2)

    class Meta(object):
        db_table = 'tblComprobanteLineas'
