from rest_framework import serializers
from presentacion.models import Presentacion
from estudio.models import Estudio
from obra_social.serializers import ObraSocialSerializer
from comprobante.serializers import ComprobanteSerializer, ComprobanteSmallSerializer


class PresentacionSmallSerializer(serializers.ModelSerializer):
    comprobante = ComprobanteSmallSerializer()
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Presentacion

    def get_estado(self, obj):
        return Presentacion.ESTADOS[obj.estado][1]


class PresentacionSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Presentacion

    def get_estado(self, obj):
        return Presentacion.ESTADOS[obj.estado][1]


class EstudioSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()

    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico',)


class PresentacionRetrieveSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = serializers.SerializerMethodField()
    estudios = EstudioSerializer(many=True)

    class Meta:
        model = Presentacion

    def get_estado(self, obj):
        return Presentacion.ESTADOS[obj.estado][1]


class EstudioEnPresentacionSerializer(serializers.Serializer):
    estudio_id = serializers.IntegerField()
    importe = serializers.DecimalField(max_digits=16, decimal_places=2)


class PresentacionCreateUpdateSerializer(serializers.Serializer):
    """
    {"fecha": 11, "estudios": [{"estudio_id": 22, "importe": 22.22}, ...]}
    o puede ser

    {"fecha": 11, estudios: [{id_estudio: {pension: 12, importe: 12, medicacion:1}}, ...]

    """
    id_presentacion = serializers.IntegerField()
    # obra social
    # fecha?
    estudios = EstudioEnPresentacionSerializer(many=True)
