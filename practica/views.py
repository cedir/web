from rest_framework import viewsets, filters
from common.drf.views import StandardResultsSetPagination
from practica.models import Practica
from practica.serializers import PracticaSerializer

class PracticaDescripcionOrCodigoMedicoFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de practicas por descripcion o codigo medico
    """
    def filter_queryset(self, request, queryset, view):
        search_text = request.query_params.get(u'descripcion')
        if search_text:
            if unicode.isdigit(search_text):
                queryset = queryset.filter(Q(codigoMedico__icontains=search_text))
            else:
                queryset = queryset.filter(descripcion__icontains=search_text)
        return queryset

class PracticaViewSet(viewsets.ModelViewSet):
    model = Practica
    queryset = Practica.objects.all()
    filter_backends = (PracticaDescripcionOrCodigoMedicoFilterBackend, )
    serializer_class = PracticaSerializer
    pagination_class = StandardResultsSetPagination