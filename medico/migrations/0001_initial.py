# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sala', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disponibilidad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia', models.CharField(max_length=20)),
                ('horaInicio', models.CharField(max_length=20, db_column=b'hora_inicio')),
                ('horaFin', models.CharField(max_length=20, db_column=b'hora_fin')),
                ('fecha', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'turnos_disponibilidad_medicos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Medico',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'idMedicoAct')),
                ('nombre', models.CharField(max_length=200, verbose_name=b'Nombre', db_column=b'nombreMedicoAct')),
                ('apellido', models.CharField(max_length=200, verbose_name=b'Apellido', db_column=b'apellidoMedicoAct')),
            ],
            options={
                'db_table': 'tblMedicosAct',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='disponibilidad',
            name='medico',
            field=models.ForeignKey(to='medico.Medico'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='disponibilidad',
            name='sala',
            field=models.ForeignKey(to='sala.Sala'),
            preserve_default=True,
        ),
    ]
