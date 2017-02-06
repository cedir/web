from rest_framework import serializers
from paciente.models import Paciente


class PacienteSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Paciente
        fields = (u'id', u'dni', u'nombre', u'apellido', u'edad')

