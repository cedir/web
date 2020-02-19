# -*- coding: utf-8
import datetime
from decimal import Decimal, ROUND_UP

from django.db import models
from django.db.models.signals import pre_save

from common.utils import generate_uuid
from medico.models import Medico, PagoMedico
from anestesista.models import Anestesista
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
    motivo = models.CharField(u'Motivo', db_column="motivoEstudio", max_length=300, blank=True, default=u'')
    informe = models.TextField(blank=True, default=u'')
    enlace_video = models.CharField(max_length=256, db_column="enlaceVideo", blank=True)
    public_id = models.CharField(max_length=35, db_column="publicID", default=generate_uuid)
    institucion = models.IntegerField(u'Institucion', db_column='institucion', default=1)

    medico = models.ForeignKey(Medico, db_column="idMedicoActuante", related_name=u'medico_actuante')
    obra_social = models.ForeignKey(ObraSocial, db_column="idObraSocial")
    medico_solicitante = models.ForeignKey(Medico, db_column="idMedicoSolicitante", related_name=u'medico_solicitante')
    presentacion = models.ForeignKey(Presentacion, db_column=u'idFacturacion', null=True, blank=True, related_name=u'estudios')
    nro_de_orden = models.CharField(db_column=u'nroDeOrden', max_length=200)
    anestesista = models.ForeignKey(Anestesista, db_column="idAnestesista", related_name=u'anestesista')

    es_pago_contra_factura = models.IntegerField(db_column="esPagoContraFactura", default=0)
    medicacion = models.ManyToManyField(Medicamento, through='Medicacion')

    fecha_cobro = models.CharField(db_column="fechaCobro", null=True, max_length=100)
    importe_estudio = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeEstudio")
    importe_medicacion = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeMedicacion")
    pago_contra_factura = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="pagoContraFactura")
    diferencia_paciente = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="diferenciaPaciente")
    pension = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    importe_pago_medico = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column=u'importePagoMedico')
    importe_pago_medico_solicitante = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column=u'importePagoMedicoSol')
    #diferencia_paciente_medicacion = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column=u'diferenciaPacienteMedicacion')
    pago_medico_actuante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoAct', null=True, blank=True, related_name=u'estudios_actuantes')
    pago_medico_solicitante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoSol', null=True, blank=True, related_name=u'estudios_solicitantes')
    importe_cobrado_pension = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeCobradoPension")
    importe_cobrado_arancel_anestesia = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeCobradoArancelAnestesia")
    importe_estudio_cobrado = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeEstudioCobrado")
    importe_medicacion_cobrado = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeMedicacionCobrado")
    arancel_anestesia = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="arancelAnestesia")

    class Meta:
        db_table = 'tblEstudios'

    def __unicode__(self):
        return u'%s %s' % (self.fecha, self.paciente)

    @property
    def fecha_vencimiento_link_video(self):
        return self.fecha + datetime.timedelta(days=MAX_DAYS_VIDEO_LINK_AVAILABLE)

    def is_link_vencido(self):
        return True if datetime.date.today() >= self.fecha_vencimiento_link_video else False

    def save(self, *args, **kwargs):
        if not self.id:  # creation
            self.set_create_defaults()
        super(Estudio, self).save(*args, **kwargs)

    def set_create_defaults(self):
        # TODO: move this to database default values on each field
        # self.motivo = u''
        # self.informe = u''
        self.nro_de_orden = u''
        # self.anestesista_id = 1
        self.es_pago_contra_factura = 0
        self.fecha_cobro = None
        self.importe_estudio = 0
        self.importe_medicacion = 0
        self.pago_contra_factura = 0
        self.diferencia_paciente = 0
        self.pension = 0
        self.importe_pago_medico = 0
        self.importe_pago_medico_solicitante = 0
        self.pago_medico_actuante = None
        self.pago_medico_solicitante = None
        self.importe_cobrado_pension = 0
        self.importe_cobrado_arancel_anestesia = 0
        self.importe_estudio_cobrado = 0
        self.importe_medicacion_cobrado = 0
        self.arancel_anestesia = 0

    @property
    def retencion_impositiva(self):
        """
        Para calculo de honorarios e informe de comprobantes.
        """
        if self.obra_social.se_presenta_por_AMR == "1" or self.obra_social.se_presenta_por_AMR == 1:
            return Decimal("0.32")
        else:
            return Decimal("0.25")

    def get_importe_total(self):
        # TODO: escribir unit tests para este metodo, no se esta usando por ahora.
        if self.fecha_cobro:
            # TODO: ver bien como se calcula el total en caso de estar cobrado.
            # hago raise por el momento, no tengo tiempo de verlo ahora
            raise NotImplementedError
        return Decimal(self.importe_estudio).quantize(Decimal('.01'), ROUND_UP) - \
               Decimal(self.diferencia_paciente).quantize(Decimal('.01'), ROUND_UP) + \
               self.arancel_anestesia + Decimal(self.pension).quantize(Decimal('.01'), ROUND_UP) + \
               self.importe_medicacion

    def get_total_medicacion(self):
        """
        Return: total medicacion sin material especifico
        NOTA: si la presentacion esta cobrada, los registros estudioXmedicamento se borran,
        por lo que perdemos el detalle de que era Medicamento y que era Material Especifico.
        En dicho caso esta funcion FALLA, ya que devuelve la suma de los dos (total) y no
        solamente Material especifico.
        """
        if self.fecha_cobro:
            raise NotImplementedError('Imposible saber el total de medicacion ya que los registros estudioXmedicamento'
                                      'se han borrado')

        total_medicacion = 0
        for medicacion in self.estudioXmedicamento.filter(medicamento__tipo=u'Medicación'):
            total_medicacion += medicacion.importe

        return Decimal(total_medicacion).quantize(Decimal('.01'), ROUND_UP)

    def get_total_material_especifico(self):
        if self.fecha_cobro:
            raise NotImplementedError('Imposible saber el total de material especifico ya que los registros'
                                      'estudioXmedicamento se han borrado')
        total = sum([medicacion.importe for medicacion in self.estudioXmedicamento.filter(medicamento__tipo=u'Mat Esp')])
        return Decimal(total).quantize(Decimal('.01'), ROUND_UP)

    def set_pago_contra_factura(self, importe):
        assert not self.presentacion_id, u'Estudio ya fue presentado y no puede modificarse'
        assert not(self.pago_medico_actuante_id or self.pago_medico_solicitante_id), u'Estudio ya fue pagado al medico y no puede modificarse'

        self.es_pago_contra_factura = 1
        self.pago_contra_factura = importe
        self.fecha_cobro = datetime.datetime.today()

    def anular_pago_contra_factura(self):
        assert bool(self.es_pago_contra_factura), u'El estudio no esta como Pago Contra Factura'
        assert not(self.pago_medico_actuante_id or self.pago_medico_solicitante_id), u'Estudio ya fue pagado al medico y no puede modificarse'
        assert self.fecha_cobro, u'El estudio no esta cobrado y por ende no es Pago Contra Factura'

        self.es_pago_contra_factura = 0
        self.pago_contra_factura = 0
        self.fecha_cobro = None


def asignar_presentacion_nula(sender, instance, **kwargs):
    """
    Esto es un hook para asgnar una presentacion nula cuando se crea un estudio.
    Esto es porque por defecto el campo idFacturacion = 0 cuando deberia ser igual a None.
    Cuando se actualice esto, este codigo puede ser eliminado.
    """
    if instance.id:
        return  # si no esta creando, no hay nada que hacer

    presentacion = Presentacion()
    presentacion.id = 0
    instance.presentacion = presentacion

pre_save.connect(asignar_presentacion_nula, sender=Estudio, dispatch_uid="asignar_presentacion_nula")


class Medicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicacion")
    medicamento = models.ForeignKey(Medicamento, db_column="idMedicamento")
    estudio = models.ForeignKey(Estudio, db_column="nroEstudio", related_name='estudioXmedicamento')
    importe = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'tblMedicacion'
