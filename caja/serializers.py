from rest_framework import serializers
from models import MovimientoCaja, TipoMovimientoCaja

class TipoMovimientoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimientoCaja
        fields = ('id', 'descripcion')

class MovimientoCajaSerializer(serializers.ModelSerializer):
    tipo = TipoMovimientoCajaSerializer()
    class Meta:
        model = MovimientoCaja
        fields = ('id', 'concepto', 'monto', 'fecha', 'hora', 'tipo', 'estado')

