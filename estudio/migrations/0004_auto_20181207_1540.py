# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-12-07 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudio', '0003_estudio_anestesista'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudio',
            name='arancel_anestesia',
            field=models.DecimalField(db_column=b'arancelAnestesia', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='diferencia_paciente',
            field=models.DecimalField(db_column=b'diferenciaPaciente', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_cobrado_arancel_anestesia',
            field=models.DecimalField(db_column=b'importeCobradoArancelAnestesia', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_cobrado_pension',
            field=models.DecimalField(db_column=b'importeCobradoPension', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_estudio',
            field=models.DecimalField(db_column=b'importeEstudio', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_estudio_cobrado',
            field=models.DecimalField(db_column=b'importeEstudioCobrado', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_medicacion',
            field=models.DecimalField(db_column=b'importeMedicacion', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_medicacion_cobrado',
            field=models.DecimalField(db_column=b'importeMedicacionCobrado', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_pago_medico',
            field=models.DecimalField(db_column='importePagoMedico', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='importe_pago_medico_solicitante',
            field=models.DecimalField(db_column='importePagoMedicoSol', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='informe',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='motivo',
            field=models.CharField(blank=True, db_column=b'motivoEstudio', default='', max_length=300, verbose_name='Motivo'),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='pago_contra_factura',
            field=models.DecimalField(db_column=b'pagoContraFactura', decimal_places=2, default=b'0.00', max_digits=16),
        ),
        migrations.AlterField(
            model_name='estudio',
            name='pension',
            field=models.DecimalField(decimal_places=2, default=b'0.00', max_digits=16),
        ),
    ]
