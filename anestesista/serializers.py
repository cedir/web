from rest_framework import serializers
from .models import Anestesista
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


class EstudioSerializer(serializers.HyperlinkedModelSerializer):
    practica = PracticaSerializer()
    
    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'practica', )


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
