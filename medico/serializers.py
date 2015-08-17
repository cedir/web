from rest_framework import serializers
from medico.models import Medico, InfoMedico
from obra_social.models import ObraSocial
from obra_social.serializers import ObraSocialSerializer


class MedicoSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Medico
        fields = (u'id', u'nombre', u'apellido', )

class InfoMedicoSerializer(serializers.HyperlinkedModelSerializer):

    medico = MedicoSerializer(required=True)
    obra_social = ObraSocialSerializer(required=True)


    class Meta:
        model = InfoMedico
        fields = (u'medico', u'obra_social', u'texto', )

