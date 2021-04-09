# pylint: disable=no-name-in-module, import-error
from rest_framework import viewsets
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaFullSerializer, MovimientoCajaImprimirSerializer
from caja.imprimir import generar_pdf_caja
from common.drf.views import StandardResultsSetPagination
from rest_framework.filters import BaseFilterBackend
from rest_framework.decorators import list_route
from distutils.util import strtobool
from django.http import HttpResponse
from datetime import datetime

class CajaConceptoFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        concepto = request.query_params.get('concepto')
        if concepto:
            queryset = queryset.filter(concepto__icontains=concepto)
        return queryset
    

class CajaMedicoFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        medico = request.query_params.get('medico')
        if medico:
            queryset = queryset.filter(medico__id=medico)
        return queryset


class CajaFechaFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        return queryset

class CajaTipoMovimientoFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tipo = request.query_params.get('tipo_movimiento')
        if tipo:
            queryset = queryset.filter(tipo__descripcion__contains=tipo)
        return queryset

class CajaIncluirEstudioFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        estudio = request.query_params.get('incluir_estudio')
        if estudio:
            queryset = queryset.exclude(estudio__isnull=strtobool(estudio))
        return queryset

class MovimientoCajaViewSet(viewsets.ModelViewSet):
    model = MovimientoCaja
    queryset = MovimientoCaja.objects.all().order_by('-id')
    serializer_class = MovimientoCajaFullSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (CajaConceptoFilterBackend, CajaMedicoFilterBackend,
        CajaFechaFilterBackend, CajaTipoMovimientoFilterBackend,
        CajaIncluirEstudioFilterBackend)

    @list_route(methods=['GET'])
    def imprimir(self, request):
        fecha=request.GET.get('fecha') # Debe poder filtrarse por cualquiera de los filtros
        movimientos = MovimientoCaja.objects.filter(fecha=fecha).order_by('-id') #Manejar cuando no haya movimientos
        movimientos_serializer = MovimientoCajaImprimirSerializer(movimientos, many=True).data
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="Detalle_Caja_{fecha}.pdf"'
        return generar_pdf_caja(response, movimientos_serializer, datetime.strptime(fecha, '%Y-%m-%d'))
