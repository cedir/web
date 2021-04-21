from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils.encoding import force_text
from django.utils.dateparse import parse_date, parse_time
from django.contrib.admin.models import ADDITION
from django.contrib.auth.models import User

from estudio.models import Estudio
from medico.models import Medico
from .models import MovimientoCaja, TipoMovimientoCaja
from practica.serializers import PracticaSerializer
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from common.utils import add_log_entry

from decimal import Decimal
from datetime import datetime
from pytz import timezone
from collections import OrderedDict

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
    tipo_id = serializers.IntegerField(required=True)
    medico_id = serializers.IntegerField(required=False)
    concepto = serializers.CharField(required=False) 
    monto = serializers.DecimalField(16, 2, required=True)

    def to_internal_value(self, data):
        datos = {}
        datos['tipo_id'] = data['tipo_id']
        datos['medico_id'] = data['medico_id']
        datos['monto'] = data['monto']
        datos['concepto'] = data['concepto']

        errors = OrderedDict()

        for field in datos:
            validate_method = getattr(self, 'validate_' + field, None)
            try:
                if validate_method:
                    datos[field] = validate_method(datos[field])
            except ValidationError as e:
                errors[field] = e.detail
            except Exception as e:
                errors[field] = str(e)
        
        if errors:
            raise ValidationError(errors)

        return datos

    def validate_medico_id(self, value):
        try:
            if value:
                value = Medico.objects.get(pk=value)
            else:
                value = None
        except Medico.DoesNotExist:
            raise ValidationError('Medico seleccionado no existe')
        return value

    def validate_monto(self, value):
        if not value:
            raise ValidationError('No existe monto')
        try:
            value = Decimal(value)
            if value == 0:
                raise ValidationError('El monto no puede ser nulo')
        except Decimal.InvalidOperation:
            raise ValidationError('El monto no es un numero')
        return value

    def validate_tipo_id(self, value):
        if not value:
            raise ValidationError("No hay tipo de movimiento")
        try:
            value = TipoMovimientoCaja.objects.get(pk=value)
        except TipoMovimientoCaja.DoesNotExist:
            raise ValidationError('Tipo de movimiento invalido')
        return value

class MovimientoCajaCreateSerializer(serializers.ModelSerializer):
    estudio_id = serializers.IntegerField(required=False)
    movimientos = MovimientoCajaCamposVariablesSerializer(many=True)
    username = serializers.CharField(required=True) 

    class Meta:
        model = MovimientoCaja
        fields = ('estudio_id', 'movimientos', 'username')

    def to_internal_value(self, data):
        datos = {}
        datos['estudio_id'] = data['estudio_id']
        datos['username'] = data['username']
        datos['movimientos'] = [MovimientoCajaCamposVariablesSerializer(data=movimiento) for movimiento in data['movimientos']]

        errors = OrderedDict()
        
        for field in datos:
            validate_method = getattr(self, 'validate_' + field, None)
            try:
                if validate_method:
                    datos[field] = validate_method(datos[field])
            except ValidationError as e:
                errors[field] = e.detail
            except Exception as e:
                errors[field] = str(e)
        
        if errors:
            raise ValidationError(errors)

        return datos
    
    def validate_username(self, value):
        try:
            value = User.objects.get(username=value)
        except User.DoesNotExist:
            raise ValidationError('Usuario invalido')
        return value

    def validate_movimientos(self, value):
        return [movimiento.validated_data for movimiento in value if movimiento.is_valid(raise_exception=True)]

    def validate_estudio_id(self, value):
        try:
            if value:
                value = Estudio.objects.get(pk=value)
            else:
                value = None
        except Estudio.DoesNotExist:
            raise ValidationError('El estudio seleccionado no existe')
        return value  

    def create(self, validated_data):
        monto_acumulado = MovimientoCaja.objects.last().monto_acumulado

        user = validated_data['username']
        estudio = validated_data['estudio_id']
        movimientos = []

        for movimiento in validated_data['movimientos']:
            tipo = movimiento['tipo_id']
            medico = movimiento['medico_id']
            concepto = movimiento['concepto']
            monto = movimiento['monto']
            monto_acumulado += monto
            movimiento = MovimientoCaja.objects.create(estudio = estudio, user = user, tipo = tipo,
            medico = medico, monto = monto, concepto = concepto, monto_acumulado = monto_acumulado)

            add_log_entry(movimiento, user, ADDITION, 'CREA')
            movimientos += [movimiento]

        return movimientos
