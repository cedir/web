# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-29 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenidos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='friendlyURL',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Friendly URL'),
        ),
    ]
