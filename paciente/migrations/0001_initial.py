# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('dni', models.IntegerField()),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre', db_column='nombres')),
                ('apellido', models.CharField(max_length=200, verbose_name='Apellido')),
                ('edad', models.IntegerField()),
                ('fechaNacimiento', models.DateField()),
                ('domicilio', models.CharField(max_length=200, verbose_name='Domicilio', db_column='direccion')),
                ('telefono', models.CharField(max_length=200, verbose_name='Telefono', db_column='tel')),
                ('sexo', models.CharField(max_length=50)),
                ('nroAfiliado', models.CharField(max_length=200, verbose_name='Nro')),
                ('email', models.CharField(max_length=200, verbose_name='Email', db_column='e_mail')),
            ],
            options={
                'db_table': 'tblPacientes',
            },
            bases=(models.Model,),
        ),
    ]
