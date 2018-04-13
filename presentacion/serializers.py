from rest_framework import serializers
from presentacion.models import Presentacion


class PresentacionSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Presentacion
        fields = (u'id', u'estado')