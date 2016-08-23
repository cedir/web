import datetime
from django.db import models
from medico.models import Medico, Anestesista, PagoMedico
from practica.models import Practica
from obra_social.models import ObraSocial
from paciente.models import Paciente
from medicamento.models import Medicamento
from presentacion.models import Presentacion


MAX_DAYS_VIDEO_LINK_AVAILABLE = 30


class Estudio(models.Model):
    id = models.AutoField(primary_key=True, db_column="nroEstudio")
    paciente = models.ForeignKey(Paciente, db_column="idPaciente")
    fechaEstudio = models.DateField(u'Fecha')
    practica = models.ForeignKey(Practica, db_column="idEstudio")
    motivoEstudio = models.CharField(u'Motivo', max_length=300, blank=True)
    informe = models.TextField(blank=True)
    enlace_video = models.CharField(max_length=256, db_column="enlaceVideo", blank=True)
    public_id = models.CharField(max_length=100, db_column="publicID")

    medico = models.ForeignKey(Medico, db_column="idMedicoActuante", related_name=u'medico_actuante')
    obraSocial = models.ForeignKey(ObraSocial, db_column="idObraSocial")
    medicoSolicitante = models.ForeignKey(Medico, db_column="idMedicoSolicitante", related_name=u'medico_solicitante')
    presentacion = models.ForeignKey(Presentacion, db_column=u'idFacturacion', null=True, blank=True, related_name=u'estudios')
    nroDeOrden = models.CharField(max_length=200)
    anestesista = models.ForeignKey(Anestesista, db_column="idAnestesista", related_name=u'anestesista')
    esPagoContraFactura = models.IntegerField()
    medicacion = models.ManyToManyField(Medicamento, through='Medicacion')

    fechaCobro = models.CharField(null=True, max_length=100)
    importeEstudio = models.FloatField()
    importeMedicacion = models.FloatField()
    pagoContraFactura = models.FloatField()
    diferenciaPaciente = models.FloatField()
    pension = models.FloatField()
    importe_pago_medico = models.FloatField(db_column=u'importePagoMedico')
    importe_pago_medico_solicitante = models.FloatField(db_column=u'importePagoMedicoSol')
    #diferencia_paciente_medicacion = models.FloatField(db_column=u'diferenciaPacienteMedicacion')
    pago_medico_actuante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoAct', null=True, blank=True, related_name=u'estudios_actuantes')
    pago_medico_solicitante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoSol', null=True, blank=True, related_name=u'estudios_solicitantes')
    importeCobradoPension = models.FloatField()
    importeCobradoArancelAnestesia = models.FloatField()
    importeEstudioCobrado = models.FloatField()
    importeMedicacionCobrado = models.FloatField()
    arancelAnestesia = models.FloatField()

    class Meta:
        db_table = 'tblEstudios'

    def __unicode__(self):
        return u'%s %s' % (self.fechaEstudio, self.paciente)

    @property
    def fecha_vencimiento_link_video(self):
        return self.fechaEstudio + datetime.timedelta(days=MAX_DAYS_VIDEO_LINK_AVAILABLE)

    def is_link_vencido(self):
        return True if datetime.date.today() >= self.fecha_vencimiento_link_video else False


class Medicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicacion")
    medicamento = models.ForeignKey(Medicamento, db_column="idMedicamento")
    estudio = models.ForeignKey(Estudio, db_column="nroEstudio", related_name='estudioXmedicamento')
    importe = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')

    class Meta:
        db_table = 'tblMedicacion'
