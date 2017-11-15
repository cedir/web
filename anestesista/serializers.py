from rest_framework import serializers
from models import Anestesista
from estudio.models import Estudio
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from caja.serializers import MovimientoCajaSerializer
from medico.serializers import MedicoSerializer
from practica.serializers import PracticaSerializer
from comprobante.serializers import ComprobanteSerializer


class AnestesistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anestesista
        fields = ('id', 'nombre', 'apellido', 'matricula', 'telefono', 'porcentaje_anestesista')


#class LineaPagoAnestesistaSerializer(serializers.HyperlinkedModelSerializer):
#    paciente = serializers.HyperlinkedRelatedField(view_name='paciente', read_only=True)
#    obra_social = serializers.HyperlinkedRelatedField(view_name='obra_social', read_only=True)
#    estudios = serializers.HyperlinkedRelatedField(many=True, view_name='estudios', read_only=True)
#    class Meta:
#        model = LineaPagoAnestesista
#        fields = ('id', 'paciente', 'obra_social', 'estudios', 'es_paciente_diferenciado', 'formula', 'formula_valorizada', 'importe', 'alicuota_iva')

#class PagoAnestesistaSerializer(serializers.HyperlinkedModelSerializer):
#    anestesista = serializers.HyperlinkedRelatedField(view_name='anestesista', read_only=True)
#    #lineas = serializers.HyperlinkedRelatedField(many=True, view_name='lineas', read_only=True)
#    class Meta:
#        model = PagoAnestesista
#        fields = ('id', 'anio', 'mes', 'anestesista', 'creado', 'modificado')


class EstudioSerializer(serializers.HyperlinkedModelSerializer):
    practica = PracticaSerializer()
    
    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'practica', )



class LineaPagoAnestesistaVMSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    paciente = PacienteSerializer()
    obra_social = ObraSocialSerializer()
    estudios = EstudioSerializer(many=True)
    movimientos_caja = MovimientoCajaSerializer(many=True)
    comprobante = ComprobanteSerializer()
    es_paciente_diferenciado = serializers.BooleanField()
    formula = serializers.CharField()
    formula_valorizada = serializers.CharField()
    importe = serializers.DecimalField(18,2)
    importe_con_iva = serializers.DecimalField(18,2)
    importe_iva = serializers.DecimalField(18,2)
    sub_total = serializers.DecimalField(18,2)
    retencion = serializers.DecimalField(18,2)
    alicuota_iva = serializers.DecimalField(4,2)


class PagoAnestesistaVMSerializer(serializers.Serializer):
    anio = serializers.IntegerField()
    mes = serializers.IntegerField()
    anestesista = AnestesistaSerializer()
    totales_ara = serializers.JSONField()
    totales_no_ara = serializers.JSONField()
    subtotales_no_ara = serializers.JSONField()
    totales_iva_no_ara = serializers.JSONField()
    lineas_ARA = LineaPagoAnestesistaVMSerializer(many=True)
    lineas_no_ARA = LineaPagoAnestesistaVMSerializer(many=True)

