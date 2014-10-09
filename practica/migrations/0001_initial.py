# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Practica',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'idEstudio')),
                ('descripcion', models.CharField(max_length=200, verbose_name=b'Descripcion', db_column=b'estudio')),
                ('codigoMedico', models.CharField(max_length=50)),
                ('abreviatura', models.CharField(max_length=20)),
                ('usedLevel', models.IntegerField()),
            ],
            options={
                'db_table': 'cedirData"."AlmacenEstudios',
            },
            bases=(models.Model,),
        ),
    ]
