from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from common.drf.views import StandardResultsSetPagination
#from django.shortcuts import render
from presentacion.models import Presentacion
from presentacion.serializers import PresentacionSerializer


class PresentacionViewSet(viewsets.ModelViewSet):

    queryset = Presentacion.objects.all()
    serializer_class = PresentacionSerializer
    filter_fields = ('obra_social',)
    ordering_fields = ('-fecha',)
    pagination_class = StandardResultsSetPagination
    page_size = 50

    @detail_route(methods=['get'])
    def get_detalle_osde(self, request, pk=None):

        presentacion = Presentacion.objects.get(pk=pk)

        csv_string = ''
        estudios = presentacion.estudios.all()

        for estudio in estudios:
            csv_string = '{}\n{}'.format(csv_string, estudio.paciente.apellido)

        response = HttpResponse(csv_string, content_type='text/csv')
        return response
