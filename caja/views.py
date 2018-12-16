from rest_framework import viewsets
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaForListadoSerializer
from common.drf.views import StandardResultsSetPagination

# Create your views here.

class MovimientoCajaViewSet(viewsets.ModelViewSet):
    model = MovimientoCaja
    queryset = MovimientoCaja.objects.all()
    serializer_class =  MovimientoCajaForListadoSerializer
    pagination_class = StandardResultsSetPagination
