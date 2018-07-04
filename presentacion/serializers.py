from rest_framework import serializers
from presentacion.models import Presentacion


class PresentacionSmallSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Presentacion
        fields = (u'id', u'estado')


class PresentacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Presentacion
        #fields = (u'id', u'estado')
