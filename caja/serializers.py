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
