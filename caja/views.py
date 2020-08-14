from rest_framework import viewsets
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaFullSerializer
from common.drf.views import StandardResultsSetPagination
from rest_framework.filters import BaseFilterBackend

class CajaConceptoFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        concepto = request.query_params.get(u'concepto')
        if concepto:
            queryset = queryset.filter(concepto__icontains=concepto)
        return queryset
    

class CajaMedicoFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        medico = request.query_params.get(u'medico')
        if medico:
            queryset = queryset.filter(medico__id=medico)
        return queryset


class CajaFechaFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        fecha_desde = request.query_params.get(u'fecha_desde')
        fecha_hasta = request.query_params.get(u'fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        return queryset

class CajaTipoMovimientoFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tipo = request.query_params.get(u'tipo_movimiento')
        if tipo:
            queryset = queryset.filter(tipo__descripcion__contains=tipo)
        return queryset

class CajaIncluirEstudioFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        estudio = request.query_params.get(u'incluir_estudio')
        if estudio:
            if estudio.lower() == 'true':
                queryset = queryset.exclude(estudio__isnull=True)
            if estudio.lower() == 'false':
                queryset = queryset.exclude(estudio__isnull=False)
        return queryset

class MovimientoCajaViewSet(viewsets.ModelViewSet):
    model = MovimientoCaja
    queryset = MovimientoCaja.objects.all().order_by('-id')
    serializer_class = MovimientoCajaFullSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (CajaConceptoFilterBackend, CajaMedicoFilterBackend,
        CajaFechaFilterBackend, CajaTipoMovimientoFilterBackend,
        CajaIncluirEstudioFilterBackend)
