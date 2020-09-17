from rest_framework import serializers
from turno.models import Turno, InfoTurno
#from medico.models import Medico
#from obra_social.models import ObraSocial
from obra_social.serializers import ObraSocialSerializer
from medico.serializers import MedicoSerializer
from practica.serializers import PracticaSerializer


class TurnoSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Turno
        fields = ('id', 'fechaTurno', 'horaInicio', )


class InfoTurnoSerializer(serializers.HyperlinkedModelSerializer):

    medico = MedicoSerializer()
    obra_sociales = ObraSocialSerializer(many=True)
    practicas = PracticaSerializer(many=True)

    class Meta:
        model = InfoTurno
        fields = ('medico', 'obra_sociales', 'practicas', 'texto', )

