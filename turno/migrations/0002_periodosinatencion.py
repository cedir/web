# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-02-09 18:47


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medico', '0003_auto_20190107_1629'),
        ('turno', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodoSinAtencion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('descripcion', models.CharField(blank=True, max_length=200, null=True)),
                ('medico', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='medico.Medico')),
            ],
        ),
    ]
