from rest_framework import serializers
from estudio.models import Estudio
from estudio.models import Medicacion
from obra_social.serializers import ObraSocialSerializer
from paciente.serializers import PacienteSerializer
from medico.serializers import MedicoSerializer
from anestesista.serializers import AnestesistaSerializer
from practica.serializers import PracticaSerializer
from medicamento.serializers import MedicamentoSerializer
from presentacion.serializers import PresentacionSerializer


class EstudioSerializer(serializers.ModelSerializer):

    obra_social = ObraSocialSerializer()
    paciente = PacienteSerializer()
    practica = PracticaSerializer()
    medico = MedicoSerializer()
    medico_solicitante = MedicoSerializer()
    anestesista = AnestesistaSerializer()
    presentacion = PresentacionSerializer()
    
    class Meta:
        model = Estudio
        fields = (u'id', u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
            u'medico_solicitante', u'anestesista', u'motivo', u'informe', u'presentacion')

class EstudioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = (u'id',u'fecha', u'paciente', u'practica', u'obra_social', u'medico',
            u'medico_solicitante', u'anestesista', u'motivo', u'informe',)

class MedicacionSerializer(serializers.HyperlinkedModelSerializer):

    medicamento = MedicamentoSerializer()

    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'estudio_id', u'importe')


class MedicacionCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Medicacion
        fields = (u'id', u'medicamento', u'importe', u'estudio')