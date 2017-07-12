from rest_framework import serializers
from comprobante.models import Comprobante, TipoComprobante, Gravado

class TipoComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoComprobante
        fields = ('id', 'nombre')


class GravadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gravado
        fields = ('id', 'descripcion', 'porcentaje')


class ComprobanteSerializer(serializers.ModelSerializer):
    tipo_comprobante = TipoComprobanteSerializer()
    gravado = GravadoSerializer()
    class Meta:
        model = Comprobante
        fields = ('id', 'tipo_comprobante', 'gravado',)

