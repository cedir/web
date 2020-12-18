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
        return [estado for estado in Presentacion.ESTADOS if estado[1] == data][0][0]

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
        fields = ('id', 'fecha', 'paciente', 'practica', 'obra_social', 'medico',
                  'medico_solicitante', 'anestesista', 'motivo', 'informe')


class EstudioRetrieveSerializer(EstudioSerializer):
    presentacion = PresentacionSmallSerializer()

    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'paciente', 'practica', 'obra_social', 'medico',
                  'medico_solicitante', 'anestesista', 'motivo', 'informe', 'presentacion',
                  'fecha_cobro', 'importe_estudio', 'importe_medicacion', 'pension', 'diferencia_paciente', 'arancel_anestesia',
                  'es_pago_contra_factura', 'pago_contra_factura')


class EstudioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = ('id','fecha', 'paciente', 'practica', 'obra_social', 'medico',
            'medico_solicitante', 'anestesista', 'motivo', 'informe', 'sucursal')

class EstudioSinPresentarSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    importe_estudio = serializers.SerializerMethodField()
    importe_medicacion = serializers.SerializerMethodField()

    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'nro_de_orden', 'paciente', 'practica',
            'medico', 'importe_estudio', 'pension', 'diferencia_paciente',
            'importe_medicacion', 'arancel_anestesia')

    def get_importe_estudio(self, estudio):
        try:
            arancel = ArancelObraSocial.objects.get(obra_social_id=estudio.obra_social_id, practica_id=estudio.practica_id).precio
        except ArancelObraSocial.DoesNotExist:
            arancel = Decimal('0.00')
        return arancel

    def get_importe_medicacion(self, estudio):
        return estudio.get_total_medicacion()

class MedicacionSerializer(serializers.HyperlinkedModelSerializer):
    medicamento = MedicamentoSerializer()

    class Meta:
        model = Medicacion
        fields = ('id', 'medicamento', 'estudio_id', 'importe')

class MedicacionCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicacion
        fields = ('id', 'medicamento', 'importe', 'estudio')



class EstudioDePresentacionRetrieveSerializer(EstudioSinPresentarSerializer):
    def get_importe_estudio(self, estudio):
        return str(estudio.importe_estudio)
    
    def get_importe_medicacion(self, estudio):
        return str(estudio.get_total_medicacion())

class MedicacionImprimirPresentacionSerializer(serializers.HyperlinkedModelSerializer):
    tipo = serializers.ReadOnlyField(source='medicamento.tipo')
    descripcion = serializers.ReadOnlyField(source='medicamento.descripcion')
    class Meta:
        model = Medicacion
        fields = ('tipo', 'descripcion', 'importe')

class EstudioDePresentacionImprimirSerializer(EstudioDePresentacionRetrieveSerializer):
    medicacion = MedicacionImprimirPresentacionSerializer( many=True)
    
    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'nro_de_orden', 'paciente', 'practica',
            'medico', 'importe_estudio', 'pension', 'diferencia_paciente',
            'importe_medicacion', 'arancel_anestesia', 'medicacion')
