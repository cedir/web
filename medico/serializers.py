from rest_framework import serializers
from medico.models import Medico


class MedicoSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Medico
        fields = (u'id', u'nombre', u'apellido', )


