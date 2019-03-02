# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-02-10 18:26
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anestesista', '0002_auto_20170711_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anestesista',
            name='porcentaje_anestesista',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=4),
        ),
    ]