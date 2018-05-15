from rest_framework import viewsets, filters
from medicamento.models import Medicamento
from medicamento.serializers import MedicamentoSerializer
from common.drf.views import StandardResultsSetPagination

class MedicamentoNombreFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de medicamentos por descripcion
    """
    def filter_queryset(self, request, queryset, view):
        nombre = request.query_params.get(u'nombre')
        if nombre:
            queryset = queryset.filter(descripcion__icontains=nombre)
        return queryset

# Create your views here.
class MedicamentoViewSet(viewsets.ModelViewSet):
    model = Medicamento
    queryset = Medicamento.objects.all()
    filter_backends = (MedicamentoNombreFilterBackend, )
    serializer_class = MedicamentoSerializer
    pagination_class = StandardResultsSetPagination
