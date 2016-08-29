from django.db import models
from medico.models import Medico
from paciente.models import Paciente
from obra_social.models import ObraSocial
from practica.models import Practica
from sala.models import Sala
from obra_social.models import ObraSocial


class Estado(models.Model):
    PENDIENTE = 1
    CONFIRMADO = 2
    ANULADO = 3

    descripcion = models.CharField(max_length=200)
    img = models.CharField(max_length=200)

    class Meta:
        db_table = 'turnos_estados'


class Turno(models.Model):
    fecha_otorgamiento = models.CharField("Fecha Otorgamiento", max_length=200, null=False, blank=False)
    fechaTurno = models.CharField("Fecha Turno", max_length=200, null=False, blank=False)
    horaInicio = models.CharField("Hora Inicio", max_length=200, null=False, blank=False)
    horaFinEstimada = models.CharField("Hora Fin Estimada", max_length=200, null=False, blank=False)
    horaFinReal = models.CharField("Hora Fin Real", max_length=200, null=False, blank=False)
    observacion = models.CharField("Observacion", max_length=200, null=False, blank=True)
    obraSocial = models.ForeignKey(ObraSocial, db_column="idObraSocial")
    paciente = models.ForeignKey(Paciente, db_column="idPaciente")
    medico = models.ForeignKey(Medico)
    sala = models.ForeignKey(Sala)
    practicas = models.ManyToManyField(Practica)
    estado = models.ForeignKey(Estado, db_column="estado_id")

    class Meta:
        db_table = 'turnos_turnos'

    def getDuracionEnMinutos(self):
        return (self.horaFinEstimada.hour * 60 + self.horaFinEstimada.minute) - (self.horaInicio.hour * 60 + self.horaInicio.minute)

    def __unicode__(self):
        return u"Turno: id={0}, fecha={1}, paciente={2}, OS={3}".format(self.id, self.fechaTurno, self.paciente, self.obraSocial)


class InfoTurno(models.Model):
    medico = models.ForeignKey(Medico, null=True, blank=True)
    obra_sociales = models.ManyToManyField(ObraSocial, null=True, blank=True)
    practicas = models.ManyToManyField(Practica, null=True, blank=True)
    texto = models.TextField()

    def get_obras_sociales_as_string(self):
        return u' - '.join([obra_social.nombre for obra_social in self.obra_sociales.all()])

    get_obras_sociales_as_string.short_description = 'Obras Sociales'

    def get_practicas_as_string(self):
        return u' - '.join([practica.abreviatura if practica.abreviatura else practica.descripcion for practica in self.practicas.all()])

    get_practicas_as_string.short_description = 'Practicas'

