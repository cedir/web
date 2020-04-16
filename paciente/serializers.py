from rest_framework import serializers
from paciente.models import Paciente
from datetime import datetime
from django.conf import settings


class PacienteSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Paciente
        fields = (u'id', u'dni', u'nombre', u'apellido', u'_edad')

class PacienteFormSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Paciente
        fields = ['dni', 'nombre', 'apellido', 'domicilio', 'telefono', 'sexo', 'fechaNacimiento', 'nroAfiliado', 'email']
    
    def validate_dni(self, dni):
        if Paciente.objects.filter(dni=dni).count() > 0:
            raise serializers.ValidationError('Error, ya existe un paciente con DNI ' + str(dni))
        return dni

    def validate_nroAfiliado(self, nroAfiliado):
        if not nroAfiliado.isalnum():
            raise serializers.ValidationError('Error, el numero de afiliado debe contener solo letras y numeros')
        return nroAfiliado

    def validate_fechaNacimiento(self, fechaNacimiento):
        return datetime.strptime(fechaNacimiento, settings.FORMAT_DATE) if fechaNacimiento else None
