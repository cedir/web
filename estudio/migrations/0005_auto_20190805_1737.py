# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-08-05 17:37


import common.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudio', '0004_auto_20190107_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudio',
            name='public_id',
            field=models.CharField(db_column='publicID', default=common.utils.generate_uuid, max_length=35),
        ),
    ]
