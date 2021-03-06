# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-29 16:04


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sala', '0001_initial'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='Anestesista',
        #     fields=[
        #         ('id', models.AutoField(db_column='idMedicoAn', primary_key=True, serialize=False)),
        #         ('nombre', models.CharField(db_column='nombreMedicoAn', max_length=200, verbose_name='Nombre')),
        #         ('apellido', models.CharField(db_column='apellidoMedicoAn', max_length=200, verbose_name='Apellido')),
        #         ('matricula', models.CharField(blank=True, db_column='nroMatricula', max_length=200, null=True, verbose_name='Matricula')),
        #         ('direccion', models.CharField(blank=True, db_column='direccionMedico', max_length=200, null=True, verbose_name='Direccion')),
        #         ('localidad', models.CharField(blank=True, db_column='localidadMedico', max_length=200, null=True, verbose_name='Localidad')),
        #         ('telefono', models.CharField(blank=True, db_column='telMedico', max_length=200, null=True, verbose_name='Telefono')),
        #         ('email', models.EmailField(blank=True, db_column='mail', max_length=200, null=True, verbose_name='E-mail')),
        #     ],
        #     options={
        #         'ordering': ['apellido'],
        #         'db_table': 'tblMedicosAnestesistas',
        #     },
        # ),
        migrations.CreateModel(
            name='Disponibilidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(max_length=20)),
                ('horaInicio', models.CharField(db_column='hora_inicio', max_length=20)),
                ('horaFin', models.CharField(db_column='hora_fin', max_length=20)),
                ('fecha', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'turnos_disponibilidad_medicos',
            },
        ),
        migrations.CreateModel(
            name='Medico',
            fields=[
                ('id', models.AutoField(db_column='idMedicoAct', primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='nombreMedicoAct', max_length=200, verbose_name='Nombre')),
                ('apellido', models.CharField(db_column='apellidoMedicoAct', max_length=200, verbose_name='Apellido')),
            ],
            options={
                'ordering': ['apellido'],
                'db_table': 'tblMedicosAct',
            },
        ),
        migrations.CreateModel(
            name='PagoMedico',
            fields=[
                ('id', models.AutoField(db_column='nroPago', primary_key=True, serialize=False)),
                ('fecha', models.DateField(db_column='fechaPago')),
                ('observacion', models.TextField(db_column='observacionPago')),
                ('medico', models.ForeignKey(db_column='idMedico', on_delete=django.db.models.deletion.CASCADE, to='medico.Medico')),
            ],
            options={
                'db_table': 'tblPagosMedicos',
            },
        ),
        migrations.AddField(
            model_name='disponibilidad',
            name='medico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medico.Medico'),
        ),
        migrations.AddField(
            model_name='disponibilidad',
            name='sala',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sala.Sala'),
        ),
    ]
