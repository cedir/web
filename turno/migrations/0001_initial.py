# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0001_initial'),
        ('obra_social', '0002_auto_20151019_1902'),
        ('medico', '0002_auto_20151019_1902'),
        ('sala', '0001_initial'),
        ('practica', '0002_auto_20150806_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(max_length=200)),
                ('img', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'turnos_estados',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha_otorgamiento', models.CharField(max_length=200, verbose_name=b'Fecha Otorgamiento')),
                ('fechaTurno', models.CharField(max_length=200, verbose_name=b'Fecha Turno')),
                ('horaInicio', models.CharField(max_length=200, verbose_name=b'Hora Inicio')),
                ('horaFinEstimada', models.CharField(max_length=200, verbose_name=b'Hora Fin Estimada')),
                ('horaFinReal', models.CharField(max_length=200, verbose_name=b'Hora Fin Real')),
                ('observacion', models.CharField(max_length=200, verbose_name=b'Observacion', blank=True)),
                ('estado', models.ForeignKey(to='turno.Estado', db_column=b'estado_id')),
                ('medico', models.ForeignKey(to='medico.Medico')),
                ('obraSocial', models.ForeignKey(to='obra_social.ObraSocial', db_column=b'idObraSocial')),
                ('paciente', models.ForeignKey(to='paciente.Paciente', db_column=b'idPaciente')),
                ('practicas', models.ManyToManyField(to='practica.Practica')),
                ('sala', models.ForeignKey(to='sala.Sala')),
            ],
            options={
                'db_table': 'turnos_turnos',
            },
            bases=(models.Model,),
        ),
    ]
