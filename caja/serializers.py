from rest_framework import serializers
from rest_framework.serializers import ValidationError
from collections import OrderedDict
from .models import MovimientoCaja, TipoMovimientoCaja
from estudio.models import Estudio
from medico.models import Medico
from practica.serializers import PracticaSerializer
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from decimal import Decimal
from datetime import date, datetime

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

class MovimientoCajaCamposVariablesSerializer(serializers.Serializer):
    tipo_id = serializers.IntegerField()
    medico_id = serializers.IntegerField(required=False)
    concepto = serializers.CharField(required=False) 
    monto = serializers.DecimalField(16, 2, required=True)

    def to_internal_value(self, data):
        data['tipo_id'] = self.validate_tipo_id(data['tipo_id'])
        data['medico_id'] = self.validate_medico_id(data['medico_id'])
        data['monto'] = self.validate_monto(data['monto'])
        return data

    def validate_medico_id(self, value):
        try:
            if value:
                value = Medico.objects.get(pk=value)
            else:
                value = None
        except Medico.DoesNotExist:
            raise ValidationError("id de medico invalida")
        return value

    def validate_monto(self, value):
        if not value:
            raise ValidationError("no existe monto")
        try:
            value = Decimal(value)
        except Decimal.InvalidOperation:
            raise ValidationError("el monto no es un numero")
        return value

    def validate_tipo_id(self, value):
        if not value:
            raise ValidationError("no existe tipo de movimiento")
        try:
            value = TipoMovimientoCaja.objects.get(pk=value)
        except TipoMovimientoCaja.DoesNotExist:
            raise ValidationError("tipo de movimiento invalido")
        return value

    def create(self, validated_data):
        return validated_data

class MovimientoCajaCreateSerializer(serializers.ModelSerializer):
    estudio_id = serializers.IntegerField(required=False)
    movimientos = MovimientoCajaCamposVariablesSerializer(many=True)

    class Meta:
        model = MovimientoCaja
        fields = ('estudio_id', 'movimientos')

    def to_internal_value(self, data):
        data['estudio_id'] = self.validate_estudio_id(data['estudio_id'])
        movimientos = [MovimientoCajaCamposVariablesSerializer(data=movimiento) for movimiento in data['movimientos']]
        for movimiento in movimientos:
            movimiento.is_valid(raise_exception=True)
        data['movimientos'] = [movimiento.save() for movimiento in movimientos]
        return data

    def validate_estudio_id(self, value):
        try:
            if value:
                value = Estudio.objects.get(pk=value)
            else:
                value = None
        except Estudio.DoesNotExist:
            raise ValidationError("id de estudio invalida")
        return value  

    def create(self, validated_data):
        monto_acumulado = MovimientoCaja.objects.last().monto_acumulado
        fecha = date.today()
        hora = datetime.now()
        estudio = validated_data['estudio_id']
        movimientos = []
        for movimiento in validated_data['movimientos']:
            tipo = movimiento['tipo_id']
            medico = movimiento['medico_id']
            concepto = movimiento['concepto']
            monto = movimiento['monto']
            monto_acumulado += monto
            movimiento = MovimientoCaja(fecha = fecha, hora = hora, estudio = estudio,
            tipo = tipo, medico = medico, monto = monto, concepto = concepto, monto_acumulado = monto_acumulado)
            movimiento.save()
            movimientos += [movimiento]
        return movimientos
