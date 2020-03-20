from decimal import Decimal
from datetime import date

from rest_framework import serializers
from rest_framework import status
from presentacion.models import Presentacion
from obra_social.models import ObraSocial
from comprobante.models import Comprobante, TipoComprobante, Gravado, LineaDeComprobante, ID_TIPO_COMPROBANTE_LIQUIDACION
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer, EstudioDePresetancionCreateUpdateSerializer
from obra_social.serializers import ObraSocialSerializer
from comprobante.serializers import ComprobanteSerializer

class EstadoField(serializers.Field):
    def to_representation(self, value):
        return Presentacion.ESTADOS[value][1]

    def to_internal_value(self, data):
        return filter(lambda estado: estado[1] == data, Presentacion.ESTADOS)[0][0]

class PresentacionSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = EstadoField()

    class Meta:
        model = Presentacion

class PresentacionRetrieveSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = EstadoField()
    estudios = EstudioDePresetancionRetrieveSerializer(many=True)

    class Meta:
        model = Presentacion

class PresentacionCreateSerializer(serializers.ModelSerializer):
    obra_social_id = serializers.IntegerField()
    estudios = serializers.ListField()

    def to_representation(self, instance):
        return {
            u'id': instance.id,
            u'obra_social_id': instance.obra_social_id,
            u'periodo': instance.periodo,
            u'fecha': instance.fecha,
        }

    def validate(self, data):
        if ObraSocial.objects.get(pk=data['obra_social_id']).is_particular_or_especial():
            raise serializers.ValidationError('La Obra Social no puede ser Particular o Particular Especial')
        for estudio_id in data['estudios']:
            estudio = Estudio.objects.get(pk=estudio_id)
            if estudio.obra_social_id != data['obra_social_id']:
                raise serializers.ValidationError('El estudio id = {0} es de una obra social distinta a la presentacion'.format(estudio_id))
            if estudio.presentacion_id != 0:
                raise serializers.ValidationError('El estudio id = {0} ya se encuentra presentado'.format(estudio_id))
        return data

    def create(self, validated_data):
        estudios = Estudio.objects.filter(id__in=validated_data['estudios'])
        del validated_data['estudios']
        presentacion = Presentacion.objects.create(
            comprobante=None,
            iva=0,
            total=sum([e.importe_estudio for e in estudios]),
            estado=Presentacion.ABIERTO,
            **validated_data
        )
        for estudio in estudios:
            estudio.presentacion = presentacion
            estudio.save()
        return presentacion

    class Meta:
        model = Presentacion
        fields = (
            u'id',
            u'obra_social_id',
            u'periodo',
            u'fecha',
            u'estudios',
        )

class PresentacionUpdateSerializer(serializers.ModelSerializer):
    estudios = serializers.ListField()

    def to_representation(self, instance):
        return {
            u'id': instance.id,
            u'obra_social_id': instance.obra_social_id,
            u'periodo': instance.periodo,
            u'fecha': instance.fecha,
        }

    def validate(self, data):
        if self.instance.estado != Presentacion.ABIERTO:
            raise serializers.ValidationError('La presentacion no se encuentra abierta')
        for estudio_id in data['estudios']:
            estudio = Estudio.objects.get(pk=estudio_id)
            if estudio.obra_social_id != self.instance.obra_social_id:
                raise serializers.ValidationError('El estudio id = {0} es de una obra social distinta a la presentacion'.format(estudio_id))
            if estudio.presentacion_id != 0 and estudio.presentacion_id != self.instance.id:
                raise serializers.ValidationError('El estudio id = {0} ya se encuentra presentado'.format(estudio_id))
        return data

    def update(self, instance, validated_data):
        instance.periodo = validated_data.get("periodo", instance.periodo)
        instance.fecha = validated_data.get("fecha", instance.fecha)
        estudios_data = Estudio.objects.filter(id__in=validated_data['estudios'])
        instance.total = sum([e.importe_estudio for e in estudios_data])
        instance.save()
        for estudio in instance.estudios.all():
            estudio.presentacion_id = 0
            estudio.save()
        for estudio in estudios_data:
            estudio.presentacion = instance
            estudio.save()
        return instance
    class Meta:
        model = Presentacion
        fields = (
            u'id',
            u'periodo',
            u'fecha',
            u'estudios',
        )