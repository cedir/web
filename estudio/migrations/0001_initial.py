# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-29 16:04


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('paciente', '0001_initial'),
        ('medicamento', '0001_initial'),
        ('practica', '0001_initial'),
        ('obra_social', '0001_initial'),
        ('medico', '0001_initial'),
        ('presentacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estudio',
            fields=[
                ('id', models.AutoField(db_column='nroEstudio', primary_key=True, serialize=False)),
                ('fecha', models.DateField(db_column='fechaEstudio', verbose_name='Fecha')),
                ('motivoEstudio', models.CharField(blank=True, max_length=300, verbose_name='Motivo')),
                ('informe', models.TextField(blank=True)),
                ('enlace_video', models.CharField(blank=True, db_column='enlaceVideo', max_length=256)),
                ('public_id', models.CharField(db_column='publicID', max_length=100)),
                ('nroDeOrden', models.CharField(max_length=200)),
                ('esPagoContraFactura', models.IntegerField()),
                ('fechaCobro', models.CharField(max_length=100, null=True)),
                ('importeEstudio', models.FloatField()),
                ('importeMedicacion', models.FloatField()),
                ('pagoContraFactura', models.FloatField()),
                ('diferenciaPaciente', models.FloatField()),
                ('pension', models.FloatField()),
                ('importe_pago_medico', models.FloatField(db_column='importePagoMedico')),
                ('importe_pago_medico_solicitante', models.FloatField(db_column='importePagoMedicoSol')),
                ('importeCobradoPension', models.FloatField()),
                ('importeCobradoArancelAnestesia', models.FloatField()),
                ('importeEstudioCobrado', models.FloatField()),
                ('importeMedicacionCobrado', models.FloatField()),
                ('arancelAnestesia', models.FloatField()),
                #('anestesista', models.ForeignKey(db_column='idAnestesista', on_delete=django.db.models.deletion.CASCADE, related_name='anestesista', to='medico.Anestesista')),
            ],
            options={
                'db_table': 'tblEstudios',
            },
        ),
        migrations.CreateModel(
            name='Medicacion',
            fields=[
                ('id', models.AutoField(db_column='idMedicacion', primary_key=True, serialize=False)),
                ('importe', models.DecimalField(decimal_places=2, default='0.00', max_digits=16)),
                ('estudio', models.ForeignKey(db_column='nroEstudio', on_delete=django.db.models.deletion.CASCADE, related_name='estudioXmedicamento', to='estudio.Estudio')),
                ('medicamento', models.ForeignKey(db_column='idMedicamento', on_delete=django.db.models.deletion.CASCADE, to='medicamento.Medicamento')),
            ],
            options={
                'db_table': 'tblMedicacion',
            },
        ),
        migrations.AddField(
            model_name='estudio',
            name='medicacion',
            field=models.ManyToManyField(through='estudio.Medicacion', to='medicamento.Medicamento'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='medico',
            field=models.ForeignKey(db_column='idMedicoActuante', on_delete=django.db.models.deletion.CASCADE, related_name='medico_actuante', to='medico.Medico'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='medicoSolicitante',
            field=models.ForeignKey(db_column='idMedicoSolicitante', on_delete=django.db.models.deletion.CASCADE, related_name='medico_solicitante', to='medico.Medico'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='obraSocial',
            field=models.ForeignKey(db_column='idObraSocial', on_delete=django.db.models.deletion.CASCADE, to='obra_social.ObraSocial'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='paciente',
            field=models.ForeignKey(db_column='idPaciente', on_delete=django.db.models.deletion.CASCADE, to='paciente.Paciente'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='pago_medico_actuante',
            field=models.ForeignKey(blank=True, db_column='nroPagoMedicoAct', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estudios_actuantes', to='medico.PagoMedico'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='pago_medico_solicitante',
            field=models.ForeignKey(blank=True, db_column='nroPagoMedicoSol', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estudios_solicitantes', to='medico.PagoMedico'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='practica',
            field=models.ForeignKey(db_column='idEstudio', on_delete=django.db.models.deletion.CASCADE, to='practica.Practica'),
        ),
        migrations.AddField(
            model_name='estudio',
            name='presentacion',
            field=models.ForeignKey(blank=True, db_column='idFacturacion', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estudios', to='presentacion.Presentacion'),
        ),
    ]
