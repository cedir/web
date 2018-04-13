from rest_framework import viewsets, filters
from common.drf.views import StandardResultsSetPagination
from practica.models import Practica
from practica.serializers import PracticaSerializer

class PracticaDescripcionFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de practicas por descripcion
    """
    def filter_queryset(self, request, queryset, view):
        descripcion = request.query_params.get(u'descripcion')
        if descripcion:
            queryset = queryset.filter(descripcion__icontains=descripcion)
        return queryset

class PracticaViewSet(viewsets.ModelViewSet):
    model = Practica
    queryset = Practica.objects.all()
    filter_backends = (PracticaDescripcionFilterBackend, )
    serializer_class = PracticaSerializer
    pagination_class = StandardResultsSetPagination