from rest_framework import serializers
from estudio.models import Estudio
from estudio.models import Medicacion
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from anestesista.serializers import AnestesistaSerializer
from practica.serializers import PracticaSerializer
from medicamento.serializers import MedicamentoSerializer
from presentacion.serializers import PresentacionSmallSerializer, PresentacionSerializer


class EstudioSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    medico_solicitante = MedicoSerializer()
    anestesista = AnestesistaSerializer()
    presentacion = PresentacionSmallSerializer()
    
    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
                  u'medico_solicitante', u'anestesista', u'motivo', u'informe', u'presentacion')


class EstudioRetrieveSerializer(EstudioSerializer):
    presentacion = PresentacionSerializer()  # TODO: definir si esto va aca o en una llamada aparte?

    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
                  u'medico_solicitante', u'anestesista', u'motivo', u'informe', u'presentacion',
                  'es_pago_contra_factura')

    # es_pago_contra_factura = models.IntegerField(db_column="esPagoContraFactura", default=0)
    # medicacion = models.ManyToManyField(Medicamento, through='Medicacion')
    #
    # fecha_cobro = models.CharField(db_column="fechaCobro", null=True, max_length=100)
    # importe_estudio = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeEstudio")
    # importe_medicacion = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeMedicacion")
    # pago_contra_factura = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="pagoContraFactura")
    # diferencia_paciente = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="diferenciaPaciente")
    # pension = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    # importe_pago_medico = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column=u'importePagoMedico')
    # importe_pago_medico_solicitante = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column=u'importePagoMedicoSol')
    # #diferencia_paciente_medicacion = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column=u'diferenciaPacienteMedicacion')
    # pago_medico_actuante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoAct', null=True, blank=True, related_name=u'estudios_actuantes')
    # pago_medico_solicitante = models.ForeignKey(PagoMedico, db_column=u'nroPagoMedicoSol', null=True, blank=True, related_name=u'estudios_solicitantes')
    # importe_cobrado_pension = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeCobradoPension")
    # importe_cobrado_arancel_anestesia = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeCobradoArancelAnestesia")
    # importe_estudio_cobrado = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeEstudioCobrado")
    # importe_medicacion_cobrado = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="importeMedicacionCobrado")
    # arancel_anestesia = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'), db_column="arancelAnestesia")


class EstudioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = (u'id',u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
            u'medico_solicitante', u'anestesista', u'motivo', u'informe',)


class MedicacionSerializer(serializers.HyperlinkedModelSerializer):
    medicamento = MedicamentoSerializer()

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'estudio_id', u'importe')


class MedicacionCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'importe', u'estudio')
