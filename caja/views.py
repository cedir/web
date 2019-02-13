from rest_framework import viewsets
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaFullSerializer
from common.drf.views import StandardResultsSetPagination


class MovimientoCajaViewSet(viewsets.ModelViewSet):
    model = MovimientoCaja
    queryset = MovimientoCaja.objects.all().order_by('-id')
    serializer_class = MovimientoCajaFullSerializer
    pagination_class = StandardResultsSetPagination
