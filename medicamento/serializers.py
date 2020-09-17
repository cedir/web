from rest_framework import serializers
from medicamento.models import Medicamento

class MedicamentoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Medicamento
        fields = ('id', 'descripcion', 'importe')