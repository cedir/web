from rest_framework import serializers
from estudio.models import Estudio, Medicacion
from presentacion.models import Presentacion
from obra_social.models import ArancelObraSocial
from obra_social.serializers import ObraSocialPensionSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from anestesista.serializers import AnestesistaSerializer
from practica.serializers import PracticaSerializer
from medicamento.serializers import MedicamentoSerializer
from comprobante.serializers import ComprobanteSmallSerializer
from decimal import Decimal

class EstadoField(serializers.Field):
    def to_representation(self, value):
        return Presentacion.ESTADOS[value][1]

    def to_internal_value(self, data):
        return filter(lambda estado: estado[1] == data, Presentacion.ESTADOS)[0][0]

class PresentacionSmallSerializer(serializers.ModelSerializer):
    comprobante = ComprobanteSmallSerializer()
    estado = EstadoField()

    class Meta:
        model = Presentacion

class EstudioSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialPensionSerializer()
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    medico_solicitante = MedicoSerializer()
    anestesista = AnestesistaSerializer()

    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
                  u'medico_solicitante', u'anestesista', u'motivo', u'informe')


class EstudioRetrieveSerializer(EstudioSerializer):
    presentacion = PresentacionSmallSerializer()

    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
                  u'medico_solicitante', u'anestesista', u'motivo', u'informe', u'presentacion',
                  u'fecha_cobro', u'importe_estudio', u'importe_medicacion', u'pension', u'diferencia_paciente', u'arancel_anestesia',
                  u'es_pago_contra_factura', u'pago_contra_factura')


class EstudioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = (u'id',u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
            u'medico_solicitante', u'anestesista', u'motivo', u'informe', u'sucursal')

class EstudioSinPresentarSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    importe_estudio = serializers.SerializerMethodField()
    importe_medicacion = serializers.SerializerMethodField()

    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'nro_de_orden', u'paciente', u'practica',
            u'medico', u'importe_estudio', u'pension', u'diferencia_paciente',
            u'importe_medicacion', u'arancel_anestesia')

    def get_importe_estudio(self, estudio):
        try:
            arancel = ArancelObraSocial.objects.get(obra_social_id=estudio.obra_social_id, practica_id=estudio.practica_id).precio
        except ArancelObraSocial.DoesNotExist:
            arancel = Decimal('0.00')
        return arancel

    def get_importe_medicacion(self, estudio):
        return estudio.get_total_medicacion()


class EstudioDePresentacionRetrieveSerializer(EstudioSinPresentarSerializer):
   def get_importe_estudio(self, estudio):
        return estudio.importe_estudio

class MedicacionSerializer(serializers.HyperlinkedModelSerializer):
    medicamento = MedicamentoSerializer()

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'estudio_id', u'importe')


class MedicacionCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'importe', u'estudio')
