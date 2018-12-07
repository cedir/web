# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-12-07 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('presentacion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentacion',
            name='comprobante',
            field=models.ForeignKey(db_column='idComprobante', on_delete=django.db.models.deletion.CASCADE, related_name='presentacion', to='comprobante.Comprobante'),
        ),
    ]
