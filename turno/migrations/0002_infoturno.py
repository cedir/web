# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('obra_social', '0002_auto_20151019_1902'),
        ('medico', '0002_auto_20151019_1902'),
        ('practica', '0002_auto_20150806_1845'),
        ('turno', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoTurno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField()),
                ('medico', models.ForeignKey(blank=True, to='medico.Medico', null=True)),
                ('obra_sociales', models.ManyToManyField(to='obra_social.ObraSocial', null=True, blank=True)),
                ('practicas', models.ManyToManyField(to='practica.Practica', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
