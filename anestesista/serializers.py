from rest_framework import serializers
from models import Anestesista, PagoAnestesista, LineaPagoAnestesista
from estudio.serializers import EstudioSerializer
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer

class AnestesistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anestesista
        fields = ('id', 'nombre', 'apellido', 'matricula', 'direccion', 'telefono', 'localidad', 'email')

class LineaPagoAnestesistaSerializer(serializers.HyperlinkedModelSerializer):
    paciente = serializers.HyperlinkedRelatedField(view_name='paciente', read_only=True)
    obra_social = serializers.HyperlinkedRelatedField(view_name='obra_social', read_only=True)
    estudios = serializers.HyperlinkedRelatedField(many=True, view_name='estudios', read_only=True)
    class Meta:
        model = LineaPagoAnestesista
        fields = ('id', 'paciente', 'obra_social', 'estudios', 'es_paciente_diferenciado', 'formula', 'formula_valorizada', 'importe', 'alicuota_iva')

class PagoAnestesistaSerializer(serializers.HyperlinkedModelSerializer):
    anestesista = serializers.HyperlinkedRelatedField(view_name='anestesista', read_only=True)
    #lineas = serializers.HyperlinkedRelatedField(many=True, view_name='lineas', read_only=True)
    class Meta:
        model = PagoAnestesista
        fields = ('id', 'anio', 'mes', 'anestesista', 'creado', 'modificado')


class LineaPagoAnestesistaVMSerializer(serializers.Serializer):
    paciente = PacienteSerializer()
    obra_social = ObraSocialSerializer()
    estudios = EstudioSerializer(many=True)
    es_paciente_diferenciado = serializers.BooleanField()
    formula = serializers.CharField()
    formula_valorizada = serializers.CharField()
    importe = serializers.DecimalField(18,2)
    alicuota_iva = serializers.DecimalField(4,2)

class PagoAnestesistaVMSerializer(serializers.Serializer):
    anio = serializers.IntegerField()
    mes = serializers.IntegerField()
    anestesista = AnestesistaSerializer()
    lineas = LineaPagoAnestesistaVMSerializer(many=True)