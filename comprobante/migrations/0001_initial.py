# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gravado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(max_length=128, db_column='descripcionGravado')),
                ('porcentaje', models.FloatField(db_column='porcentajeGravado')),
            ],
            options={
                'db_table': 'tblGravado',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LineaDeComprobante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('concepto', models.CharField(max_length=128)),
                ('sub_total', models.FloatField(db_column='subtotal')),
                ('iva', models.FloatField(db_column='importeIVA')),
                ('importe_neto', models.FloatField(db_column='importeNeto')),
            ],
            options={
                'db_table': 'tblComprobanteLineas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoComprobante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=128, db_column='tipoComprobante')),
            ],
            options={
                'db_table': 'tblComprobantesTipo',
            },
            bases=(models.Model,),
        ),
       migrations.CreateModel(
            name='Comprobante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre_cliente', models.CharField(max_length=128, db_column='nombreCliente')),
                ('domicilio_cliente', models.CharField(max_length=128, db_column='domicilioCliente')),
                ('nro_cuit', models.CharField(max_length=128, db_column='nroCuit')),
                ('gravado_paciente', models.CharField(max_length=128, db_column='gravadoPaciente')),
                ('condicion_fiscal', models.CharField(max_length=128, db_column='condicionFiscal')),
                ('responsable', models.CharField(max_length=128)),
                ('sub_tipo', models.CharField(max_length=50, db_column='subTipo')),
                ('estado', models.CharField(max_length=50)),
                ('numero', models.IntegerField(db_column='nroComprobante')),
                ('nro_terminal', models.SmallIntegerField(default=1, db_column='nroTerminal')),
                ('total_facturado', models.FloatField(default=0, db_column='totalFacturado')),
                ('total_cobrado', models.FloatField(db_column='totalCobrado')),
                ('fecha_emision', models.DateField(db_column='fechaEmision')),
                ('fecha_recepcion', models.DateField(db_column='fechaRecepcion')),
                ('cae', models.TextField(db_column=b'CAE', blank=True)),
                ('vencimiento_cae', models.DateField(null=True, db_column=b'vencimientoCAE', blank=True)),
                ('tipo_comprobante', models.ForeignKey(to='comprobante.TipoComprobante', db_column='idTipoComprobante')),
                ('gravado', models.ForeignKey(db_column='gravado', blank=True, to='comprobante.Gravado', null=True)),
                ('factura', models.ForeignKey(db_column='idFactura', blank=True, to='comprobante.Comprobante', null=True)),
            ],
            options={
                'db_table': 'tblComprobantes',
                'permissions': (('informe_ventas', 'Permite generar el informe de ventas.'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='lineadecomprobante',
            name='comprobante',
            field=models.ForeignKey(related_name='lineas', db_column='idComprobante', to='comprobante.Comprobante'),
            preserve_default=True,
        ),
    ]
