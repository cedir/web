from rest_framework import serializers
from paciente.models import Paciente
from datetime import date, datetime
from django.conf import settings


class PacienteSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Paciente
        fields = (u'id', u'dni', u'nombre', u'apellido', u'_edad')

class PacienteFormSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Paciente
        fields = ['id', 'dni', 'nombre', 'apellido', 'domicilio', 'telefono', 'sexo', 'fechaNacimiento', 'nroAfiliado', 'infExtra', 'email']

    def to_internal_value(self, data):
        dni = data.get(u'dni')
        fecha_nacimiento = data.get(u'fecha_nacimiento')

        if fecha_nacimiento:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, settings.FORMAT_DATE).date()

        datos = {
            'nombre': data.get('nombre'),
            'apellido': data.get('apellido'),
            'nroAfiliado': data.get(u'nro_afiliado', u''),
            'infExtra': data.get(u'inf_extra', u''),
            'domicilio': data.get(u'domicilio', u''),
            'sexo': data.get(u'sexo', u''),
            'telefono': data.get(u'telefono', u''),
            'dni': int(dni) if dni else 0,
            'fechaNacimiento': fecha_nacimiento or None,
            'email': data.get(u'email'),
        }

        return super(PacienteFormSerializer, self).to_internal_value(datos)

    def validate_nroAfiliado(self, nroAfiliado):
        if not all(x.isalnum() or x.isspace() for x in nroAfiliado):
            raise serializers.ValidationError('Error, el numero de afiliado debe contener solo letras y numeros')
        return nroAfiliado
