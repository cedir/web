# pylint: disable=no-name-in-module, import-error
from rest_framework import viewsets, status, serializers
from caja.models import MovimientoCaja
from caja.serializers import MovimientoCajaFullSerializer, MovimientoCajaImprimirSerializer, MovimientoCajaCreateSerializer
from caja.imprimir import generar_pdf_caja

from common.drf.views import StandardResultsSetPagination
from distutils.util import strtobool

from typing import Dict
from datetime import date, datetime
from decimal import Decimal

from django.http import HttpResponse, JsonResponse

from rest_framework.serializers import ValidationError
from rest_framework.filters import BaseFilterBackend
from rest_framework.decorators import list_route

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


    def create(self, request):
        try:

            data = {'username': request.user.get_username(), **request.data}
            movimientos_serializer = MovimientoCajaCreateSerializer(data=data)

            if not movimientos_serializer.is_valid():
                raise serializers.ValidationError(movimientos_serializer.errors)

            movimientos = movimientos_serializer.save()
            response = JsonResponse({}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as ex:
            response = JsonResponse({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            response = JsonResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @list_route(methods=['GET'])
    def imprimir(self, request):
        try:
            movimientos = self.filter_queryset(self.queryset)

            if len(movimientos) == 0:
                raise ValidationError('Debe seleccionarse una fecha donde hayan movimientos')
        
            movimientos_serializer = MovimientoCajaImprimirSerializer(movimientos, many=True).data
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'filename="Detalle_Caja_Generado_{date.today()}.pdf"'

            fecha = movimientos.first().fecha if movimientos.first().fecha == movimientos.last().fecha else ''
            response = generar_pdf_caja(response, movimientos_serializer, fecha, MovimientoCaja.objects.last().monto_acumulado)
        except ValidationError as ex:
            response = JsonResponse({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            response = JsonResponse({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response
