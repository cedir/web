from rest_framework import serializers
from presentacion.models import Presentacion
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer, EstudioDePresetancionCreateUpdateSerializer
from obra_social.serializers import ObraSocialSerializer
from comprobante.serializers import ComprobanteSerializer, ComprobanteSmallSerializer

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

class PresentacionCreateUpdateSerializer(serializers.Serializer):
    estado = EstadoField()
    estudios = EstudioDePresetancionCreateUpdateSerializer(many=True)

    class Meta:
        model = Presentacion
        fields = (u'obra_social_id', u'periodo', u'fecha', u'estado', u'estudios', u'comprobante')