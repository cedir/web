from django.db import models
from sala.models import Sala
from obra_social.models import ObraSocial


class Medico(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicoAct")
    nombre = models.CharField("Nombre",max_length=200, db_column="nombreMedicoAct")
    apellido = models.CharField("Apellido",max_length=200, db_column="apellidoMedicoAct")
    #domicilio = models.CharField("Domicilio",max_length=200, db_column="direccionMedico")
    #localidad = models.CharField("Localidad", db_column="localidadMedico",max_length=200)
    #telefono = models.CharField("Telefono",max_length=200, db_column="telMedico")
    #matricula = models.CharField("Matricula",max_length=200, db_column="nroMatricula")
    #mail = models.CharField("Mail",max_length=200, db_column="mail")

    def __unicode__ (self):
        return u'%s, %s' % (self.apellido, self.nombre, )

    class Meta:
        db_table = 'cedirData\".\"tblMedicosAct'
        ordering = [u'apellido']


class Disponibilidad(models.Model):
    dia = models.CharField(max_length=20)
    horaInicio = models.CharField(db_column="hora_inicio", max_length=20)
    horaFin = models.CharField(db_column="hora_fin", max_length=20)
    fecha = models.CharField(max_length=100)
    medico = models.ForeignKey(Medico)
    sala = models.ForeignKey(Sala)

    def getDuracionEnMinutos(self):
        return (self.horaFin.hour * 60 + self.horaFin.minute) - (self.horaInicio.hour * 60 + self.horaInicio.minute)

    class Meta:
        db_table = 'cedirData\".\"turnos_disponibilidad_medicos'


class InfoMedico(models.Model):
    medico = models.ForeignKey(Medico)
    obra_social = models.ForeignKey(ObraSocial)
    texto = models.TextField()

