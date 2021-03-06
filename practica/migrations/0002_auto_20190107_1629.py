# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-01-07 16:29


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='practica',
            name='codigo_medico_osde',
            field=models.CharField(blank=True, db_column='codigoMedicoOSDE', max_length=50),
        ),
        migrations.AlterField(
            model_name='practica',
            name='abreviatura',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='practica',
            name='codigoMedico',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='practica',
            name='usedLevel',
            field=models.IntegerField(default=0),
        ),
    ]
