# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-10 18:46


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anestesista', '0001_initial'),
        ('estudio', '0002_auto_20161125_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudio',
            name='anestesista',
            field=models.ForeignKey(db_column='idAnestesista', default=1, on_delete=django.db.models.deletion.CASCADE, related_name='anestesista', to='anestesista.Anestesista'),
            preserve_default=False,
        ),
    ]
