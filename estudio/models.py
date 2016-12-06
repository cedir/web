import datetime
from django.db import models
from django.db.models.signals import pre_save
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
    fecha = models.DateField(u'Fecha', db_column="fechaEstudio")
    practica = models.ForeignKey(Practica, db_column="idEstudio")
    motivo = models.CharField(u'Motivo', db_column="motivoEstudio", max_length=300, blank=True)
    informe = models.TextField(blank=True)
    enlace_video = models.CharField(max_length=256, db_column="enlaceVideo", blank=True)
    public_id = models.CharField(max_length=100, db_column="publicID")

    medico = models.ForeignKey(Medico, db_column="idMedicoActuante", related_name=u'medico_actuante')
    obra_social = models.ForeignKey(ObraSocial, db_column="idObraSocial")
    medico_solicitante = models.ForeignKey(Medico, db_column="idMedicoSolicitante", related_name=u'medico_solicitante')
    presentacion = models.ForeignKey(Presentacion, db_column=u'idFacturacion', null=True, blank=True, related_name=u'estudios')
    nro_de_orden = models.CharField(db_column=u'nroDeOrden', max_length=200)
    anestesista = models.ForeignKey(Anestesista, db_column="idAnestesista", related_name=u'anestesista')
    es_pago_contra_factura = models.IntegerField(db_column="esPagoContraFactura", default=0)
    medicacion = models.ManyToManyField(Medicamento, through='Medicacion')

    fecha_cobro = models.CharField(db_column="fechaCobro", null=True, max_length=100)
    importe_estudio = models.FloatField(db_column="importeEstudio")
    importe_medicacion = models.FloatField(db_column="importeMedicacion")
    pago_contra_factura = models.FloatField(db_column="pagoContraFactura")
    diferencia_paciente = models.FloatField(db_column="diferenciaPaciente")
    pension = models.FloatField()
    importe_pago_medico = models.FloatField(db_column=u'importePagoMedico')
    importe_pago_medico_solicitante = models.FloatField(db_column=u'importePagoMedicoSol')
    #diferencia_paciente_medicacion = models.FloatField(db_column=u'diferenciaPacienteMedicacion')
    pago_medico_actuante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoAct', null=True, blank=True, related_name=u'estudios_actuantes')
    pago_medico_solicitante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoSol', null=True, blank=True, related_name=u'estudios_solicitantes')
    importe_cobrado_pension = models.FloatField(db_column="importeCobradoPension")
    importe_cobrado_arancel_anestesia = models.FloatField(db_column="importeCobradoArancelAnestesia")
    importe_estudio_cobrado = models.FloatField(db_column="importeEstudioCobrado")
    importe_medicacion_cobrado = models.FloatField(db_column="importeMedicacionCobrado")
    arancel_anestesia = models.FloatField(db_column="arancelAnestesia")

    class Meta:
        db_table = 'tblEstudios'

    def __unicode__(self):
        return u'%s %s' % (self.fecha, self.paciente)

    @property
    def fecha_vencimiento_link_video(self):
        return self.fecha + datetime.timedelta(days=MAX_DAYS_VIDEO_LINK_AVAILABLE)

    def is_link_vencido(self):
        return True if datetime.date.today() >= self.fecha_vencimiento_link_video else False


def asignar_presentacion_nula(sender, instance, **kwargs):
    """
    Esto es un hook para asgnar una presentacion nula cuando se crea un estudio.
    Esto es porque por defecto el campo idFacturacion = 0 cuando deberia ser igual a None.
    Cuando se actualice esto, este codigo puede ser eliminado.
    """
    if instance.id:
        return  # is no esta creando, no hay nada que hacer

    presentacion = Presentacion()
    presentacion.id = 0
    instance.presentacion = presentacion

pre_save.connect(asignar_presentacion_nula, sender=Estudio, dispatch_uid="asignar_presentacion_nula")


class Medicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicacion")
    medicamento = models.ForeignKey(Medicamento, db_column="idMedicamento")
    estudio = models.ForeignKey(Estudio, db_column="nroEstudio", related_name='estudioXmedicamento')
    importe = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')

    class Meta:
        db_table = 'tblMedicacion'
