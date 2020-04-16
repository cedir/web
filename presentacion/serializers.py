from decimal import Decimal
from datetime import date

from rest_framework import serializers
from rest_framework import status
from presentacion.models import Presentacion
from obra_social.models import ObraSocial
from comprobante.models import Comprobante, TipoComprobante, Gravado, LineaDeComprobante, ID_TIPO_COMPROBANTE_LIQUIDACION
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer
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
        for estudio_data in data['estudios']:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            if estudio.obra_social_id != data['obra_social_id']:
                raise serializers.ValidationError('El estudio id = {0} es de una obra social distinta a la presentacion'.format(estudio.id))
            if estudio.presentacion_id != 0:
                raise serializers.ValidationError('El estudio id = {0} ya se encuentra presentado'.format(estudio.id))
        return data

    def create(self, validated_data):
        estudios_data = validated_data['estudios']
        estudios = Estudio.objects.filter(id__in=[e["id"] for e in estudios_data])
        del validated_data['estudios']
        presentacion = Presentacion.objects.create(
            comprobante=None,
            iva=0,
            estado=Presentacion.ABIERTO,
            **validated_data
        )
        for estudio_data in estudios_data:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            estudio.presentacion = presentacion
            estudio.nro_de_orden = estudio_data.get("nro_de_orden", estudio.nro_de_orden)
            estudio.importe_estudio = estudio_data.get("importe_estudio", estudio.importe_estudio)
            estudio.pension = estudio_data.get("pension", estudio.pension)
            estudio.diferencia_paciente = estudio_data.get("diferencia_paciente", estudio.diferencia_paciente)
            estudio.importe_medicacion = estudio_data.get("medicacion", estudio.importe_medicacion)
            estudio.arancel_anestesia = estudio_data.get("arancel_anestesia", estudio.arancel_anestesia)
            estudio.save()
        presentacion.total_facturado = sum([e.get_importe_total() for e in estudios])
        presentacion.save()
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
        for estudio_data in data['estudios']:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            if estudio.obra_social_id != self.instance.obra_social_id:
                raise serializers.ValidationError('El estudio id = {0} es de una obra social distinta a la presentacion'.format(estudio.id))
            if estudio.presentacion_id != 0 and estudio.presentacion_id != self.instance.id:
                raise serializers.ValidationError('El estudio id = {0} ya se encuentra presentado'.format(estudio.id))
        return data

    def update(self, instance, validated_data):
        instance.periodo = validated_data.get("periodo", instance.periodo)
        instance.fecha = validated_data.get("fecha", instance.fecha)
        estudios_data = validated_data['estudios']
        estudios = Estudio.objects.filter(id__in=[e["id"] for e in estudios_data])
        for estudio in instance.estudios.all():
            estudio.presentacion_id = 0
            estudio.save()
        for estudio_data in estudios_data:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            estudio.presentacion = instance
            estudio.nro_de_orden = estudio_data.get("nro_de_orden", estudio.nro_de_orden)
            estudio.importe_estudio = estudio_data.get("importe_estudio", estudio.importe_estudio)
            estudio.pension = estudio_data.get("pension", estudio.pension)
            estudio.diferencia_paciente = estudio_data.get("diferencia_paciente", estudio.diferencia_paciente)
            estudio.importe_medicacion = estudio_data.get("medicacion", estudio.importe_medicacion)
            estudio.arancel_anestesia = estudio_data.get("arancel_anestesia", estudio.arancel_anestesia)
            estudio.save()
        instance.total_facturado = sum([e.get_importe_total() for e in estudios])
        instance.save()
        return instance
    class Meta:
        model = Presentacion
        fields = (
            u'id',
            u'periodo',
            u'fecha',
            u'estudios',
        )