from rest_framework import serializers
from presentacion.models import Presentacion
from obra_social.serializers import ObraSocialSerializer
from comprobante.serializers import ComprobanteSerializer


class PresentacionSmallSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Presentacion
        fields = (u'id', u'estado')


class PresentacionSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Presentacion

    def get_estado(self, obj):
        return Presentacion.ESTADOS[obj.estado][1]
