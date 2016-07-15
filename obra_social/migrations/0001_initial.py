# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ObraSocial',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'idObraSocial')),
                ('nombre', models.CharField(max_length=200, db_column=b'obraSocial')),
            ],
            options={
                'db_table': 'AlmacenObraSocial',
            },
            bases=(models.Model,),
        ),
    ]
