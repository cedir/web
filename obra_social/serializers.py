from rest_framework import serializers
from obra_social.models import ObraSocial


class ObraSocialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ObraSocial
        fields = (u'id', u'nombre', )

