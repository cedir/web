from rest_framework import serializers
from models import MovimientoCaja, TipoMovimientoCaja
from estudio.models import Estudio
from practica.serializers import PracticaSerializer
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer

class TipoMovimientoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimientoCaja
        fields = ('id', 'descripcion')

class EstudioCajaSerializer(serializers.ModelSerializer):
    practica = PracticaSerializer()
    obra_social = ObraSocialSerializer()
    paciente = PacienteSerializer()
    medico = MedicoSerializer()
    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'practica', u'obra_social', u'paciente', u'medico')

class MovimientoCajaSerializer(serializers.ModelSerializer):
    tipo = TipoMovimientoCajaSerializer()
    class Meta:
        model = MovimientoCaja
        fields = (u'id', u'concepto', u'monto', u'fecha', u'hora', u'tipo', u'estado')

class MovimientoCajaForListadoSerializer(serializers.ModelSerializer):
    tipo = TipoMovimientoCajaSerializer()
    estudio = EstudioCajaSerializer()
    class Meta:
        model = MovimientoCaja
        fields = (u'id', u'concepto', u'estudio', u'monto', u'monto_acumulado', u'fecha', u'hora', u'tipo', u'estado')

