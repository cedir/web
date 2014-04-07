# -*- coding: utf-8 -*-
from django.db import models
from django.http import HttpResponse
from managers.model.personas import *
from datetime import datetime, date, time

class Sala(models.Model):
  id = models.AutoField(primary_key=True)
  nombre = models.CharField()
  observaciones = models.CharField()

  class Meta:
    db_table = 'cedirData\".\"turnos_salas'

class Practica(models.Model):
  id = models.AutoField(primary_key=True, db_column="idEstudio")
  descripcion = models.CharField("Descripcion",max_length=200, db_column="estudio")
  codigoMedico = models.CharField()
  abreviatura = models.CharField()
  usedLevel = models.IntegerField()
  #duracion = models.CharField("Duracion",max_length=200, null=False,blank=False)

  class Meta:
    db_table = 'cedirData\".\"AlmacenEstudios'

class Disponibilidad(models.Model):
  dia = models.CharField()
  horaInicio = models.CharField(db_column="hora_inicio")
  horaFin = models.CharField(db_column="hora_fin")
  fecha = models.CharField()
  medico = models.ForeignKey(Medico)
  sala = models.ForeignKey(Sala)

  def getDuracionEnMinutos(self):
    return (self.horaFin.hour * 60 + self.horaFin.minute) - (self.horaInicio.hour * 60 + self.horaInicio.minute)

  class Meta:
    db_table = 'cedirData\".\"turnos_disponibilidad_medicos'


class ObraSocial(models.Model):
  id = models.AutoField(primary_key=True, db_column="idObraSocial")
  nombre = models.CharField(db_column="obraSocial")
  #direccion = models.CharField()
  #telefono = models.CharField()
  #localidad = models.CharField()
  #observaciones = models.CharField()

  class Meta:
    db_table = 'cedirData\".\"AlmacenObraSocial'

class Estado(models.Model):
  descripcion = models.CharField()
  img = models.CharField()

  class Meta:
    db_table = 'cedirData\".\"turnos_estados'

class Turno(models.Model):
  fecha_otorgamiento = models.CharField("Fecha Otorgamiento",max_length=200, null=False,blank=False)
  fechaTurno = models.CharField("Fecha Turno",max_length=200, null=False,blank=False)
  horaInicio = models.CharField("Hora Inicio",max_length=200, null=False,blank=False)
  horaFinEstimada = models.CharField("Hora Fin Estimada",max_length=200, null=False,blank=False)
  horaFinReal = models.CharField("Hora Fin Real",max_length=200, null=False,blank=False)
  observacion = models.CharField("Observacion",max_length=200, null=False,blank=True)
  obraSocial = models.ForeignKey(ObraSocial, db_column="idObraSocial")
  paciente = models.ForeignKey(Paciente,db_column="idPaciente") #ex paciente_id
  medico = models.ForeignKey(Medico)
  sala = models.ForeignKey(Sala)
  practicas = models.ManyToManyField(Practica)
  estado = models.ForeignKey(Estado,db_column="estado_id")
  #idPaciente = models.IntegerField()

  class Meta:
    db_table = 'cedirData\".\"turnos_turnos'

  def getDuracionEnMinutos(self):
    return (self.horaFinEstimada.hour * 60 + self.horaFinEstimada.minute) - (self.horaInicio.hour * 60 + self.horaInicio.minute)

  def __unicode__(self):
    return str(self.id)

class AuditLog(models.Model):
  userActionId = models.IntegerField()
  objectTypeId = models.IntegerField()
  objectId = models.IntegerField()
  dateTime = models.CharField(max_length=200, null=False,blank=False)
  observacion = models.CharField()
  user = models.ForeignKey(Usuario,db_column="userId")

  class Meta:
    db_table = 'cedirData\".\"AuditUserActionsLog'

    
#---------------- Estudios ------------------------#
    
class Estudio(models.Model):
  id = models.AutoField(primary_key=True, db_column="nroEstudio")
  paciente = models.ForeignKey(Paciente,db_column="idPaciente")
  fechaEstudio = models.CharField() #TODO:Esto deberia ser DATE
  practica = models.ForeignKey(Estado,db_column="idEstudio")
  motivoEstudio = models.CharField()
  informe = models.CharField()

  class Meta:
    db_table = 'cedirData\".\"tblEstudios'

class DetalleEstudio(models.Model):
  id = models.AutoField(primary_key=True, db_column="nroEstudio")
  medico = models.ForeignKey(Medico, db_column="idMedicoActuante")
  obraSocial = models.ForeignKey(ObraSocial, db_column="idObraSocial")
  medicoSolicitante = models.ForeignKey(Medico, db_column="idMedicoSolicitante")
  idFacturacion = models.IntegerField()
  nroDeOrden = models.CharField()
  idAnestesista = models.IntegerField()
  esPagoContraFactura = models.IntegerField()

  class Meta:
    db_table = 'cedirData\".\"tblDetalleEstudio'

class PagoCobroEstudio(models.Model):
  id = models.AutoField(primary_key=True, db_column="nroEstudio")
  fechaCobro = models.CharField(null=True)
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
