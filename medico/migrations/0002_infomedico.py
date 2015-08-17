# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('obra_social', '0001_initial'),
        ('medico', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoMedico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField()),
                ('medico', models.ForeignKey(to='medico.Medico')),
                ('obra_social', models.ForeignKey(to='obra_social.ObraSocial')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
