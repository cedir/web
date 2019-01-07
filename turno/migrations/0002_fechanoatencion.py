# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-01-03 22:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medico', '0003_auto_20190103_2241'),
        ('turno', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FechaNoAtencion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField(verbose_name=b'Fecha Inicio')),
                ('fecha_fin', models.DateTimeField(verbose_name=b'Fecha Fin')),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medico.Medico')),
            ],
            options={
                'db_table': 'turnos_fecha_no_atencion',
            },
        ),
    ]