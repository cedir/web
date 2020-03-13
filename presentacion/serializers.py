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

class PresentacionCreateUpdateSerializer(serializers.ModelSerializer):
    obra_social_id = serializers.IntegerField()
    estudios = serializers.ListField()
    comprobante = serializers.DictField()

    def to_representation(self, instance):
        return {
            u'id': instance.id,
            u'obra_social_id': instance.obra_social_id,
            u'periodo': instance.periodo,
            u'fecha': instance.fecha,
            u'comprobante': ComprobanteSerializer(instance.comprobante).data
        }

    def validate(self, data):
        if ObraSocial.objects.get(pk=data['obra_social_id']).is_particular_or_especial():
            raise serializers.ValidationError('La Obra Social no puede ser Particular o Particular Especial')
        for estudio_data in data['estudios']:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            if estudio.obra_social_id != data['obra_social_id']:
                raise serializers.ValidationError('La presentacion contiene un estudio de otra Obra Social')
        return data

    def create(self, validated_data):
        obra_social = ObraSocial.objects.get(pk=validated_data['obra_social_id'])
        periodo = validated_data['periodo']
        estudios_data = validated_data['estudios']
        presentacion = Presentacion.objects.create(
            comprobante=None,
            estado=Presentacion.PENDIENTE,
            **validated_data
        )
        for estudio_data in estudios_data:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            estudio.nro_de_orden = estudio_data['nro_de_orden']
            estudio.importe_estudio = estudio_data['importe_estudio']
            estudio.pension = estudio_data['pension']
            estudio.diferencia_paciente = estudio_data['diferencia_paciente']
            estudio.arancel_anestesia = estudio_data['arancel_anestesia']
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
            u'comprobante'
        )