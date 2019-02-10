# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-10 18:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anestesista',
            fields=[
                ('id', models.AutoField(db_column='idMedicoAn', primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='nombreMedicoAn', max_length=200, verbose_name='Nombre')),
                ('apellido', models.CharField(db_column='apellidoMedicoAn', max_length=200, verbose_name='Apellido')),
                ('matricula', models.CharField(blank=True, db_column='nroMatricula', max_length=200, null=True, verbose_name='Matricula')),
                ('direccion', models.CharField(blank=True, db_column='direccionMedico', max_length=200, null=True, verbose_name='Direccion')),
                ('localidad', models.CharField(blank=True, db_column='localidadMedico', max_length=200, null=True, verbose_name='Localidad')),
                ('telefono', models.CharField(blank=True, db_column='telMedico', max_length=200, null=True, verbose_name='Telefono')),
                ('email', models.EmailField(blank=True, db_column='mail', max_length=200, null=True, verbose_name='E-mail')),
                ('porcentaje_anestesista', models.DecimalField(decimal_places=2, default='0.00', max_digits=2)),
            ],
            options={
                'ordering': ['apellido'],
                #'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Complejidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importe', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'db_table': 'tblComplejidades',
                #'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ComplejidadEstudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estudios', models.CharField(blank=True, max_length=500, null=True)),
                ('formula', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'db_table': 'tblComplejidadEstudios',
                #'managed': False,
            },
        ),
    ]
