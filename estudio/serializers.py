from rest_framework import serializers
from estudio.models import Estudio, Medicacion
from presentacion.models import Presentacion
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from anestesista.serializers import AnestesistaSerializer
from practica.serializers import PracticaSerializer
from medicamento.serializers import MedicamentoSerializer
from comprobante.serializers import ComprobanteSmallSerializer

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
    obra_social = ObraSocialSerializer()
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

class EstudioDePresetancionRetrieveSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()

    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'nro_de_orden', u'paciente', u'practica',
            u'medico', u'importe_estudio', u'pension', u'diferencia_paciente',
            u'importe_medicacion', u'arancel_anestesia')


class MedicacionSerializer(serializers.HyperlinkedModelSerializer):
    medicamento = MedicamentoSerializer()

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'estudio_id', u'importe')


class MedicacionCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'importe', u'estudio')
