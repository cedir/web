# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('observaciones', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'cedirData"."turnos_salas',
            },
            bases=(models.Model,),
        ),
    ]
