from rest_framework import serializers
from obra_social.models import ObraSocial


class ObraSocialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ObraSocial
        fields = ('id', 'nombre', )

class ObraSocialPensionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ObraSocial
        fields = ('id', 'nombre', 'valor_aproximado_pension', )
