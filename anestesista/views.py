# -*- coding: utf-8 -*-
import copy
from decimal import Decimal, ROUND_UP
from itertools import groupby
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from estudio.models import Estudio
from anestesista.models import Anestesista, PagoAnestesistaVM, LineaPagoAnestesistaVM, Complejidad
from anestesista.serializers import PagoAnestesistaVMSerializer
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
    pago = PagoAnestesistaVM()
    pago.anestesista = Anestesista.objects.get(id=id_anestesista)
    pago.anio = anio
    pago.mes = mes
    pago.porcentaje_anestesista = pago.anestesista.porcentaje_anestesista
    pago.lineas_ARA = []
    pago.lineas_no_ARA = []
    pago.totales_ara = {}
    pago.totales_honorarios_ara = {}
    pago.totales_no_ara = {}
    pago.totales_honorarios_no_ara = {}

    estudios = Estudio.objects.filter(anestesista_id=id_anestesista, fecha__year=anio, fecha__month=mes).order_by('fecha','paciente','obra_social')
    grupos_de_estudios = groupby(estudios, lambda e: (e.fecha, e.paciente, e.obra_social))

    for (fecha, paciente, obra_social), grupo in grupos_de_estudios:
        # grupo contiene los estudios del grupo. La tupla (fecha, paciente, obra_social) coinciden para el grupo
        linea = LineaPagoAnestesistaVM()
        linea.fecha = fecha
        linea.paciente = paciente
        linea.obra_social = obra_social
        linea.es_paciente_diferenciado = 1 <= linea.paciente.get_edad() <=12 or linea.paciente.get_edad() >= 70
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

        linea_ara = None
        linea_no_ara = None
        if obra_social.se_presenta_por_ARA:
            linea_ara = linea
            if linea.movimientos_caja:  # R1: si hay movimientos en cualquier estudio, la linea debe ir tanto en ARA como en NO ARA
                linea_no_ara = copy.deepcopy(linea)
        else:
            linea_no_ara = linea

        ara = result.get('ara')
        if linea_ara:
            linea_ara.alicuota_iva = ara.get('alicuota_iva')
            linea_ara.importe = ara.get('importe')
            linea_ara.sub_total = ara.get('sub_total')
            linea_ara.retencion = ara.get('retencion')
            linea_ara.importe_iva = ara.get('importe_iva')
            linea_ara.importe_con_iva = ara.get('importe_con_iva')

            iva_key = u'{}'.format(linea_ara.alicuota_iva)
            pago.totales_ara[iva_key] = linea_ara.importe_con_iva + pago.totales_ara.get(iva_key, 0)
            pago.totales_honorarios_ara[iva_key] = linea_ara.retencion + pago.totales_honorarios_ara.get(iva_key, 0)

            pago.lineas_ARA.append(linea_ara)
            
        no_ara = result.get('no_ara')
        if linea_no_ara:
            linea_no_ara.comprobante = no_ara.get('comprobante')
            linea_no_ara.alicuota_iva = no_ara.get('alicuota_iva')
            linea_no_ara.importe = no_ara.get('importe')
            linea_no_ara.sub_total = no_ara.get('sub_total')
            linea_no_ara.retencion = no_ara.get('a_pagar')
            linea_no_ara.importe_iva = no_ara.get('importe_iva')
            linea_no_ara.importe_con_iva = no_ara.get('importe_con_iva')

            iva_key = u'{}'.format(linea_no_ara.alicuota_iva)
            pago.totales_no_ara[iva_key] = linea_no_ara.importe_con_iva + pago.totales_no_ara.get(iva_key, 0)
            pago.totales_honorarios_no_ara[iva_key] = linea_no_ara.retencion + pago.totales_honorarios_no_ara.get(iva_key, 0)

            pago.lineas_no_ARA.append(linea_no_ara)
            
    serializer = PagoAnestesistaVMSerializer(pago, context={'request': request})
    return JSONResponse(serializer.data)

