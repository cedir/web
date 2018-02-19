from rest_framework import serializers
from estudio.models import Estudio
from estudio.models import Medicacion
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from practica.serializers import PracticaSerializer
from medicamento.serializers import MedicamentoSerializer


class EstudioSerializer(serializers.ModelSerializer):

    obra_social = ObraSocialSerializer()
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    medico_solicitante = MedicoSerializer()
    
    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico', u'medico_solicitante',)

class EstudioLiteSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Estudio
        fields = (u'id',)

class EstudioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = (u'fecha', u'paciente', u'practica', u'obra_social', u'medico', u'medico_solicitante',)

class MedicacionSerializer(serializers.HyperlinkedModelSerializer):

    medicamento = MedicamentoSerializer()
    estudio = EstudioLiteSerializer()

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'estudio', u'importe')


class MedicacionCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'importe', u'estudio')