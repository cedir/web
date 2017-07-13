from rest_framework import serializers
from comprobante.models import Comprobante, LineaDeComprobante, TipoComprobante, Gravado

class TipoComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoComprobante
        fields = ('id', 'nombre')


class GravadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gravado
        fields = ('id', 'descripcion', 'porcentaje')


class LineaDeComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaDeComprobante
        fields = ('id', 'concepto', 'sub_total', 'iva', 'importe_neto')


class ComprobanteSerializer(serializers.ModelSerializer):
    tipo_comprobante = TipoComprobanteSerializer()
    gravado = GravadoSerializer()
    lineas = LineaDeComprobanteSerializer(many=True)
    class Meta:
        model = Comprobante
        fields = ('id', 'nombre_cliente', 'sub_tipo', 'numero', 'nro_terminal', 'total_facturado', 'total_cobrado', 'fecha_emision', 'tipo_comprobante', 'gravado', 'lineas')

