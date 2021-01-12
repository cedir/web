# -*- coding: utf-8 -*-
import copy
from decimal import Decimal, ROUND_UP
from itertools import groupby
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters
from django.db.models import Q
from rest_framework.renderers import JSONRenderer

from estudio.models import Estudio, ID_SUCURSAL_CEDIR
from anestesista.models import Anestesista, PagoAnestesistaVM, LineaPagoAnestesistaVM, Complejidad, SIN_ANESTESIA
from anestesista.serializers import AnestesistaSerializer, PagoAnestesistaVMSerializer
from anestesista.calculador_honorarios.calculador_honorarios import CalculadorHonorariosAnestesista


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def generar_vista_nuevo_pago(request, id_anestesista, anio, mes):
    sucursal = request.GET.get('sucursal', ID_SUCURSAL_CEDIR)
    pago = PagoAnestesistaVM()
    pago.anestesista = Anestesista.objects.get(id=id_anestesista)
    pago.anio = anio
    pago.mes = mes
    pago.porcentaje_anestesista = pago.anestesista.porcentaje_anestesista
    pago.lineas_ARA = []
    pago.lineas_no_ARA = []
    pago.totales_ara = {}  # {"iva": XX, "subtotal": "XX", "total": XX}
    pago.totales_no_ara = {}  # {"iva00": XX, "iva105": XX, "iva21": XX}
    pago.subtotales_no_ara = {}  # {"iva00": XX, "iva105": XX, "iva21": XX}
    pago.totales_iva_no_ara = {}  # {"iva00": XX, "iva105": XX, "iva21": XX}

    estudios = Estudio.objects.filter(anestesista_id=id_anestesista, fecha__year=anio, fecha__month=mes, sucursal=sucursal).order_by('fecha','paciente','obra_social')
    grupos_de_estudios = groupby(estudios, lambda e: (e.fecha, e.paciente, e.obra_social))

    for (fecha, paciente, obra_social), grupo in grupos_de_estudios:
        # grupo contiene los estudios del grupo. La tupla (fecha, paciente, obra_social) coinciden para el grupo
        linea = LineaPagoAnestesistaVM()
        linea.fecha = fecha
        linea.paciente = paciente
        linea.obra_social = obra_social
        if int(id_anestesista) != SIN_ANESTESIA:
            linea.es_paciente_diferenciado = 1 <= linea.paciente.get_edad() <=12 or linea.paciente.get_edad() >= 70
        else:
            linea.es_paciente_diferenciado = False
        linea.comprobante = None

        linea.importe = 0
        linea.alicuota_iva = 0
        linea.formula = '0'
        linea.formula_valorizada = '0'
        linea.sub_total = 0
        linea.importe_con_iva = 0
        linea.importe_iva = 0
        linea.retencion = 0
        linea.movimientos_caja = []

        linea.estudios = list(grupo)

        calculador_honorarios = CalculadorHonorariosAnestesista(pago.anestesista, linea.estudios, linea.obra_social)
        try:
            result = calculador_honorarios.calculate()
        except Complejidad.DoesNotExist:
            pago.lineas_ARA.append(linea)
            continue

        linea.formula = result.get('formula')
        linea.formula_valorizada = result.get('formula_valorizada')
        linea.movimientos_caja = result.get('movimientos_caja')

        ara = result.get('ara')
        if ara:
            linea_ara = linea
            linea_ara.alicuota_iva = ara.get('alicuota_iva')
            linea_ara.importe = ara.get('importe')
            linea_ara.sub_total = ara.get('sub_total')
            linea_ara.retencion = ara.get('retencion')

            pago.totales_ara['subtotal'] = linea_ara.retencion + pago.totales_ara.get('subtotal', Decimal(0))

            # calculo total a continuacion podria hacerse fuera del IF ya que solo el subtotal final sirve
            pago.totales_ara['iva'] = pago.totales_ara['subtotal'] * linea_ara.alicuota_iva / Decimal(100)
            pago.totales_ara['total'] = pago.totales_ara['subtotal'] + pago.totales_ara['iva']

            pago.lineas_ARA.append(linea_ara)
            
        no_ara = result.get('no_ara')
        if no_ara:
            linea_no_ara = copy.deepcopy(linea) if ara else linea
            linea_no_ara.comprobante = no_ara.get('comprobante')
            linea_no_ara.alicuota_iva = no_ara.get('alicuota_iva')
            linea_no_ara.importe = no_ara.get('importe')
            linea_no_ara.sub_total = no_ara.get('sub_total')
            linea_no_ara.retencion = no_ara.get('a_pagar')

            iva_key = 'iva{}'.format(linea_no_ara.alicuota_iva).replace('.', '')  # TODO: warn! el FE esta esperando especificamente 0, 10.5 y 21. De existir otro IVA va a haber que agregarlo en ULI
            pago.subtotales_no_ara[iva_key] = linea_no_ara.retencion + pago.subtotales_no_ara.get(iva_key, Decimal(0))

            # calculo total a continuacion podria hacerse fuera del IF ya que solo el subtotal final sirve
            pago.totales_iva_no_ara[iva_key] = pago.subtotales_no_ara[iva_key] * linea_no_ara.alicuota_iva / Decimal(100)
            pago.totales_no_ara[iva_key] = pago.subtotales_no_ara[iva_key] + pago.totales_iva_no_ara[iva_key]

            pago.lineas_no_ARA.append(linea_no_ara)
            
    # round totals
    for k in pago.totales_ara:
        pago.totales_ara[k] = pago.totales_ara[k].quantize(Decimal('.01'), ROUND_UP)
    for k in pago.subtotales_no_ara:
        pago.subtotales_no_ara[k] = pago.subtotales_no_ara[k].quantize(Decimal('.01'), ROUND_UP)
    for k in pago.totales_iva_no_ara:
        pago.totales_iva_no_ara[k] = pago.totales_iva_no_ara[k].quantize(Decimal('.01'), ROUND_UP)
    for k in pago.totales_no_ara:
        pago.totales_no_ara[k] = pago.totales_no_ara[k].quantize(Decimal('.01'), ROUND_UP)

    serializer = PagoAnestesistaVMSerializer(pago, context={'request': request})
    return JSONResponse(serializer.data)

class AnestesistaNombreApellidoFilterBackend(filters.BaseFilterBackend):
    
    """
    Filtro de anestesista por nombre o apellido
    """
    def filter_queryset(self, request, queryset, view):
        search_text = request.query_params.get('search_text')


        if search_text:
            if str.isdigit(search_text):
                queryset = queryset.filter(Q(matricula__icontains=search_text))
            else:
                search_params = [x.strip() for x in search_text.split(',')]
                nomOApe1 = search_params[0]
                nomOApe2 = search_params[1] if len(search_params) >= 2 else ''
                queryset = queryset.filter((Q(nombre__icontains=nomOApe1) & Q(apellido__icontains=nomOApe2)) |
                    (Q(nombre__icontains=nomOApe2) & Q(apellido__icontains=nomOApe1)))
        return queryset

class AnastesistaViewSet(viewsets.ModelViewSet):
    model = Anestesista
    queryset = Anestesista.objects.all()
    serializer_class = AnestesistaSerializer
    filter_backends = (AnestesistaNombreApellidoFilterBackend, )
    pagination_class = None