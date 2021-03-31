# pylint: disable=no-name-in-module, import-error
from rest_framework import viewsets, status, serializers
from django.http import JsonResponse
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaFullSerializer, MovimientoCajaCreateSerializer
from common.drf.views import StandardResultsSetPagination
from rest_framework.filters import BaseFilterBackend
from distutils.util import strtobool
from typing import Dict
from datetime import date, datetime
from decimal import Decimal

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
    serializers = {
        'create': MovimientoCajaCreateSerializer,
    }

    def create(self, request):
        try:
            movimientos_serializer = MovimientoCajaCreateSerializer(data=request.data)
            if not movimientos_serializer.is_valid():
                raise serializers.ValidationError(movimientos_serializer.errors)

            movimientos = movimientos_serializer.save()
            response = JsonResponse({}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as ex:
            response = JsonResponse({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            response = JsonResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    # def create(self, request):
    #     request = MovimientoCajaCreateSerializer(request)
    #     try:
    #         request: Dict = request.data
    #         fecha = date.today()
    #         hora = datetime.now()
    #         estudio = request['estudio']
    #         movimientos = request['movimientos']
    #         monto_acumulado = MovimientoCaja.objects.last().monto_acumulado
            
    #         for movimiento in movimientos:
    #             concepto = movimiento['concepto']
    #             tipo = movimiento['tipo']
    #             medico = movimiento['medico']
    #             monto = Decimal(movimiento['monto']) # corroborar
    #             monto_acumulado = monto + monto_acumulado
    #             print(medico)
    #             movimiento_caja = MovimientoCaja(
    #                 medico = medico, estudio = estudio,
    #                 concepto = concepto, fecha = fecha,
    #                 hora = hora, tipo = tipo, monto = monto,
    #                 monto_acumulado = monto_acumulado,
    #             )
    #             print('aaaaaaaa')
    #             movimiento_caja.is_valid(raise_exception=True)
    #             movimiento_caja.save()

    #         response = JsonResponse({}, status=status.HTTP_200_OK)

    #     except Exception as ex:
    #         response = JsonResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     return response
