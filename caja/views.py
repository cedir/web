from rest_framework import viewsets
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaSerializer
from common.drf.views import CajaPagination

# Create your views here.

class MovimientoCajaViewSet(viewsets.ModelViewSet):
    model = MovimientoCaja
    queryset = MovimientoCaja.objects.all()
    serializer_class =  MovimientoCajaSerializer
    pagination_class = CajaPagination


