from django.shortcuts import render
from rest_framework import viewsets
from medico.models import InfoMedico
from medico.serializers import InfoMedicoSerializer


class InfoMedicoViewSet(viewsets.ModelViewSet):
    model = InfoMedico
    queryset = InfoMedico.objects.all()
    serializer_class = InfoMedicoSerializer
    filter_fields = (u'medico', u'obra_social')

