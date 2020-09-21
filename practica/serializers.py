from rest_framework import serializers
from practica.models import Practica


class PracticaSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Practica
        fields = ('id', 'descripcion', 'codigoMedico', 'abreviatura')

