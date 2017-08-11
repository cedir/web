# -*- coding: utf-8 -*-
import copy
from decimal import Decimal, ROUND_UP
from itertools import groupby
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from estudio.models import Estudio
from anestesista.models import Anestesista, Complejidad, PagoAnestesistaVM, LineaPagoAnestesistaVM
from anestesista.serializers import AnestesistaSerializer, PagoAnestesistaVMSerializer, LineaPagoAnestesistaVMSerializer
from anestesista.utils import get_complejidad_a_aplicar, eval_expr


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def generar_vista_nuevo_pago(request, id_anestesista, anio, mes):
    TIPO_MOV_CAJA_HONORARIO_ANESTESISTA = 3
    TIPO_MOV_CAJA_COSEGURO = 10
    PORCENTAJE_DESCUENTO_CEDIR = Decimal('0.35')
    SIMARA_ID = 6
    SIMARA_IMPORTE_C2 = u'1742.0'

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
    complejidades = Complejidad.objects.all()
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

        complejidad = get_complejidad_a_aplicar(linea.estudios)
        if not complejidad:
            pago.lineas_ARA.append(linea)
            continue

        # obtenemos la fórmula de cálculo de la complejidad
        linea.formula = complejidad.formula.lower() if complejidad else '0'
        linea.formula_valorizada = complejidad.formula.lower() if complejidad else '0'

        # reemplazamos en la fórmula los valores de cada complejidad
        if obra_social.id == SIMARA_ID:
            # esta es una excepcion que pronto se va a sacar. Simara tiene valor distinto para c2
            linea.formula_valorizada = linea.formula_valorizada.replace('c2', SIMARA_IMPORTE_C2)
        for c in complejidades:
            linea.formula_valorizada = linea.formula_valorizada.replace('c{0}'.format(c.id), c.importe)

        # obtenermos el importe de la serie de estudios
        linea.importe = Decimal(eval_expr(linea.formula_valorizada))

        # obtenemos los movimientos de caja asociados
        linea.movimientos_caja = [mov
            for estudio in linea.estudios
            for mov     in estudio.movimientos_caja.filter(tipo_id__in=[TIPO_MOV_CAJA_HONORARIO_ANESTESISTA, TIPO_MOV_CAJA_COSEGURO])
        ]
        total_mov_caja = sum(mov.monto for mov in linea.movimientos_caja)

        linea_ara = None
        linea_no_ara = None
        if obra_social.se_presenta_por_ARA:
            linea_ara = linea
            if linea.movimientos_caja:  # R1: si hay movimientos en cualquier estudio, la linea debe ir tanto en ARA como en NO ARA
                linea_no_ara = copy.deepcopy(linea)
        else:
            linea_no_ara = linea

        if linea_ara:
            linea_ara.alicuota_iva = Decimal('21.0')
            linea_ara.importe *= linea_ara.get_coeficiente_paciente_diferenciado()
 
            if linea.movimientos_caja:
                linea_ara.importe = linea_ara.importe - total_mov_caja

            linea_ara.sub_total = linea_ara.importe - (linea_ara.importe * PORCENTAJE_DESCUENTO_CEDIR)
            linea_ara.sub_total = linea_ara.sub_total.quantize(Decimal('.01'), ROUND_UP)
            linea_ara.retencion = linea_ara.sub_total * pago.porcentaje_anestesista / 100

            # totales
            linea_ara.importe_iva = linea_ara.importe * linea_ara.alicuota_iva / 100
            linea_ara.importe_con_iva = linea_ara.importe + linea_ara.importe_iva
            iva_key = u'{}'.format(linea_ara.alicuota_iva)
            pago.totales_ara[iva_key] = linea_ara.importe_con_iva + pago.totales_ara.get(iva_key, 0)
            pago.totales_honorarios_ara[iva_key] = linea_ara.retencion + pago.totales_honorarios_ara.get(iva_key, 0)

            pago.lineas_ARA.append(linea_ara)
            
        if linea_no_ara:
            if obra_social.se_presenta_por_ARA: # (es duplicado de una linea_ara)
                linea_ara.importe = total_mov_caja.quantize(Decimal('.01'), ROUND_UP)
                linea_no_ara.alicuota_iva = Decimal('0.0')  # es cero porque ya esta incluido en el monto del mov. de caja
            else:
                if obra_social.is_particular_or_especial():
                    comprobante = linea_no_ara.get_comprobante_particular()
                else:
                    comprobante = linea_no_ara.get_comprobante_desde_facturacion()
                
                linea_no_ara.alicuota_iva = comprobante.gravado.porcentaje if comprobante and comprobante.tipo_comprobante.nombre != 'Liquidacion' else Decimal('0.0')
                linea_no_ara.importe *= linea_no_ara.get_coeficiente_paciente_diferenciado()
                linea_no_ara.comprobante = comprobante

            linea_no_ara.sub_total = linea_no_ara.importe - (linea_no_ara.importe * PORCENTAJE_DESCUENTO_CEDIR)
            linea_no_ara.sub_total = linea_no_ara.sub_total.quantize(Decimal('.01'), ROUND_UP)
            linea_no_ara.retencion = linea_no_ara.sub_total * (100 - pago.porcentaje_anestesista) / 100
            
            # totales
            linea_no_ara.importe_iva = linea_no_ara.importe * Decimal(linea_no_ara.alicuota_iva) / 100
            linea_no_ara.importe_con_iva = linea_no_ara.importe + linea_no_ara.importe_iva
            iva_key = u'{}'.format(linea_no_ara.alicuota_iva)
            pago.totales_no_ara[iva_key] = linea_no_ara.importe_con_iva + pago.totales_no_ara.get(iva_key, 0)
            pago.totales_honorarios_no_ara[iva_key] = linea_no_ara.retencion + pago.totales_honorarios_no_ara.get(iva_key, 0)

            pago.lineas_no_ARA.append(linea_no_ara)
            
    serializer = PagoAnestesistaVMSerializer(pago, context={'request': request})
    return JSONResponse(serializer.data)

