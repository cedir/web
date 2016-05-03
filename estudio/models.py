import datetime
from django.db import models
from medico.models import Medico
from practica.models import Practica
from obra_social.models import ObraSocial
from paciente.models import Paciente


MAX_DAYS_VIDEO_LINK_AVAILABLE = 30


class Estudio(models.Model):
    id = models.AutoField(primary_key=True, db_column="nroEstudio")
    paciente = models.ForeignKey(Paciente, db_column="idPaciente")
    fechaEstudio = models.DateField()
    practica = models.ForeignKey(Practica, db_column="idEstudio")  # TODO: esto estaba asociado a Estado en vez de practica. Por que??? ver si no estaba rompiendo
    motivoEstudio = models.CharField(max_length=300)
    informe = models.TextField()
    enlace_video = models.CharField(max_length=256, db_column="enlaceVideo", null=True)
    public_id = models.CharField(max_length=100, db_column="publicID", null=True)

    medico = models.ForeignKey(Medico, db_column="idMedicoActuante", related_name=u'medico_actuante')
    obraSocial = models.ForeignKey(ObraSocial, db_column="idObraSocial")
    medicoSolicitante = models.ForeignKey(Medico, db_column="idMedicoSolicitante", related_name=u'medico_solicitante')
    idFacturacion = models.IntegerField()
    nroDeOrden = models.CharField(max_length=200)
    idAnestesista = models.IntegerField()
    esPagoContraFactura = models.IntegerField()
    #estudio = models.ForeignKey(Estudio, db_column="nro")

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
        db_table = 'tblEstudios'

    @property
    def fecha_vencimiento_link_video(self):
        return self.fechaEstudio + datetime.timedelta(days=MAX_DAYS_VIDEO_LINK_AVAILABLE)

    def is_link_vencido(self):
        return True if datetime.date.today() >= self.fecha_vencimiento_link_video else False

    def save(self, *args, **kwargs):
        """
        Disable save from admin. Passing param 'force' to allow saving from code.
        """
        if self.pk is None or kwargs.pop(u'force', None):
            super(Estudio, self).save(*args, **kwargs)



