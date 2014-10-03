from django.db import models
from medico.models import Medico
from practica.models import Practica
from obra_social.models import ObraSocial
from paciente.models import Paciente


class Estudio(models.Model):
    id = models.AutoField(primary_key=True, db_column="nroEstudio")
    paciente = models.ForeignKey(Paciente, db_column="idPaciente")
    fechaEstudio = models.CharField(max_length=100)  # TODO:Esto deberia ser DATE
    practica = models.ForeignKey(Practica, db_column="idEstudio")  # TODO: esto estaba asociado a Estado en vez de practica. Por que??? ver si no estaba rompiendo
    motivoEstudio = models.CharField(max_length=300)
    informe = models.TextField()

    class Meta:
        db_table = 'cedirData\".\"tblEstudios'


class DetalleEstudio(models.Model):
    id = models.AutoField(primary_key=True, db_column="nroEstudio")
    medico = models.ForeignKey(Medico, db_column="idMedicoActuante", related_name=u'medico_actuante')
    obraSocial = models.ForeignKey(ObraSocial, db_column="idObraSocial")
    medicoSolicitante = models.ForeignKey(Medico, db_column="idMedicoSolicitante", related_name=u'medico_solicitante')
    idFacturacion = models.IntegerField()
    nroDeOrden = models.CharField(max_length=200)
    idAnestesista = models.IntegerField()
    esPagoContraFactura = models.IntegerField()

    class Meta:
        db_table = 'cedirData\".\"tblDetalleEstudio'


class PagoCobroEstudio(models.Model):
    id = models.AutoField(primary_key=True, db_column="nroEstudio")
    fechaCobro = models.CharField(null=True, max_length=100)
    importeEstudio = models.FloatField()
    importeMedicacion = models.FloatField()
    pagoContraFactura = models.FloatField()
    diferenciaPaciente = models.FloatField()
    pension = models.FloatField()
    importePagoMedico = models.FloatField()
    importePagoMedicoSol = models.FloatField()
    #diferenciaPacienteMedicacion = models.FloatField(null=True)
    #nroPagoMedicoAct = models.IntegerField(null=True)
    #nroPagoMedicoSol = models.IntegerField(null=True)
    importeCobradoPension = models.FloatField()
    importeCobradoArancelAnestesia = models.FloatField()
    importeEstudioCobrado = models.FloatField()
    importeMedicacionCobrado = models.FloatField()
    arancelAnestesia = models.FloatField()

    class Meta:
        db_table = 'cedirData\".\"tblPagoCobroEstudio'
