# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-18 20:13


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MovimientoCaja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concepto', models.TextField(blank=True)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('hora', models.TimeField()),
                ('monto', models.DecimalField(blank=True, db_column='monto', decimal_places=2, max_digits=10, null=True)),
                ('estado', models.NullBooleanField()),
            ],
            options={
                'db_table': 'tblCajaMovimientos',
                # 'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TipoMovimientoCaja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'tblCajaTipoDeMovimientos',
                # 'managed': False,
            },
        ),
    ]
