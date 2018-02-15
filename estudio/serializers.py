from rest_framework import serializers
from estudio.models import Estudio
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from practica.serializers import PracticaSerializer


class EstudioSerializer(serializers.ModelSerializer):

    obra_social = ObraSocialSerializer()
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    medico_solicitante = MedicoSerializer()
    
    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico', u'medico_solicitante',)


class EstudioCreateUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Estudio
            fields = (u'fecha', u'paciente', u'practica', u'obra_social', u'medico', u'medico_solicitante',)
