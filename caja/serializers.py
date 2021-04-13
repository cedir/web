from rest_framework import serializers
from .models import MovimientoCaja, TipoMovimientoCaja
from estudio.models import Estudio
from practica.serializers import PracticaSerializer
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer


class TipoMovimientoCajaSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoMovimientoCaja
        fields = ('id', 'descripcion')


class MovimientoCajaSerializer(serializers.ModelSerializer):
    tipo = TipoMovimientoCajaSerializer()

    class Meta:
        model = MovimientoCaja
        fields = ('id', 'concepto', 'monto', 'fecha', 'hora', 'tipo')


class EstudioCajaSerializer(serializers.ModelSerializer):
    practica = PracticaSerializer()
    obra_social = ObraSocialSerializer()
    paciente = PacienteSerializer()
    medico = MedicoSerializer()

    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'practica', 'obra_social', 'paciente', 'medico')


class MovimientoCajaFullSerializer(serializers.ModelSerializer):
    tipo = TipoMovimientoCajaSerializer()
    estudio = EstudioCajaSerializer()
    medico = MedicoSerializer()

    class Meta:
        model = MovimientoCaja
        fields = ('id', 'concepto', 'estudio', 'monto', 'monto_acumulado', 'fecha', 'hora', 'tipo', 'medico')

class MovimientoCajaImprimirSerializer(serializers.ModelSerializer):
    hora = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    paciente = serializers.SerializerMethodField()
    obra_social = serializers.SerializerMethodField()
    medico = serializers.SerializerMethodField()
    practica = serializers.SerializerMethodField()

    class Meta:
        model = MovimientoCaja
        fields = ('hora', 'usuario', 'tipo', 'paciente', 'obra_social',
                  'medico', 'practica', 'concepto', 'monto', 'monto_acumulado')

    def get_hora(self, obj):
        return obj.hora or ''

    def get_tipo(self, obj):
        return obj.tipo.descripcion or ''

    def get_usuario(self, obj):
        return ''

    def get_paciente(self, obj):
        return f'{obj.estudio.paciente.apellido}, {obj.estudio.paciente.nombre}' if obj.estudio else ''

    def get_obra_social(self, obj):
        return obj.estudio.obra_social.nombre if obj.estudio else ''

    def get_medico(self, obj):
        medico = obj.medico or (obj.estudio and obj.estudio.medico)
        return f'{medico.apellido}, {medico.nombre}' if medico else ''

    def get_practica(self, obj):
        return obj.estudio.practica.descripcion if obj.estudio else ''
