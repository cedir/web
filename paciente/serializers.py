from rest_framework import serializers
from paciente.models import Paciente
from datetime import date, datetime
from django.conf import settings


class PacienteSerializer(serializers.HyperlinkedModelSerializer):
    domicilio = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = ('id', 'dni', 'nombre', 'apellido', '_edad', 'nroAfiliado', 'informacion_extra', 'domicilio')

    def get_domicilio(self, obj):
        return obj.domicilio

class PacienteFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paciente
        fields = ['id', 'dni', 'nombre', 'apellido', 'domicilio', 'telefono', 'sexo', 'fechaNacimiento', 'nroAfiliado', 'informacion_extra', 'email']

    def to_internal_value(self, data):
        dni = data.get('dni')
        fecha_nacimiento = data.get('fecha_nacimiento')

        if fecha_nacimiento:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, settings.FORMAT_DATE).date()

        datos = {
            'nombre': data.get('nombre'),
            'apellido': data.get('apellido'),
            'nroAfiliado': data.get('nro_afiliado', ''),
            'informacion_extra': data.get('informacion_extra', ''),
            'domicilio': data.get('domicilio', ''),
            'sexo': data.get('sexo', ''),
            'telefono': data.get('telefono', ''),
            'dni': int(dni) if dni else 0,
            'fechaNacimiento': fecha_nacimiento or None,
            'email': data.get('email'),
        }

        return super(PacienteFormSerializer, self).to_internal_value(datos)
