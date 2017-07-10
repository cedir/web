# -*- coding: utf-8 -*-
import copy
from decimal import Decimal
from itertools import groupby
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from estudio.models import Estudio
from estudio.serializers import EstudioSerializer
#from anestesista.models import Anestesista, ComplejidadEstudio, Complejidad, PagoAnestesistaVM, LineaPagoAnestesistaVM
#from anestesista.serializers import AnestesistaSerializer, PagoAnestesistaVMSerializer, LineaPagoAnestesistaVMSerializer


def eval_expr(expr):
    import ast
    import operator as op

    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
        ast.USub: op.neg}
    def eval_(node):
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return operators[type(node.op)](eval_(node.left), eval_(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_(node.operand))
        else:
            raise TypeError(node)

    return eval_(ast.parse(expr, mode='eval').body)

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def get_complejidad_a_aplicar(estudios):
    """
    """
    # generamos el patrón de búsqueda para la complejidad
    # (es una lista de codigos destudios ordenada y separada por coma)
    estudios_id = ','.join([str(id) for id in sorted(set([estudio.practica.id for estudio in estudios]))])

    # obtenemos la complejidad de la serie de estudios
    # TODO: revisar contains vs igual y get- Agrega manejo de error y devolver None - ver que hace el codigo .net
    complejidad = ComplejidadEstudio.objects.filter(estudios__contains=estudios_id).first()
    return complejidad


def pago(request, id_anestesista, anio, mes):
    TIPO_MOV_CAJA_HONORARIO_ANESTESISTA = 3
    TIPO_MOV_CAJA_COSEGURO = 10

    pago = PagoAnestesistaVM()

    pago.anestesista = Anestesista.objects.get(id=id_anestesista)
    pago.anio = anio
    pago.mes = mes
    pago.porcentaje_anestesista = pago.anestesista.porcentaje_anestesista  # TODO: agregar este campo en anestesista (falta crear la migration)

    # obtenemos los estudios por anestesista, año y mes
    estudios = Estudio.objects.filter(anestesista_id=id_anestesista, fecha__year=anio, fecha__month=mes).order_by('fecha','paciente','obra_social')
    complejidades = Complejidad.objects.all()

    # agrupamos en paquetes fecha/paciente/obra_social
    grupos_de_estudios = groupby(estudios, lambda e: (e.fecha, e.paciente, e.obra_social))

    pago.lineas_ARA = []
    pago.lineas_no_ARA = []

    #import ipdb; ipdb.set_trace()

    # por cada paquete
    for (fecha, paciente, obra_social), grupo in grupos_de_estudios:
        linea = LineaPagoAnestesistaVM()
        linea.fecha = fecha
        linea.paciente = paciente
        linea.obra_social = obra_social
        linea.es_paciente_diferenciado = 1 <= linea.paciente.get_edad() <=12 or linea.paciente.get_edad() >= 70

        estudios = sorted(grupo, key=lambda estudio: estudio.practica.id)
        linea.estudios = estudios

        complejidad = get_complejidad_a_aplicar(linea.estudios)
        if not complejidad:
            linea.importe = 0
            linea.alicuota_iva = 0
            pago.lineas_ARA.append(linea)
            continue

        # obtenemos la fórmula de cálculo de la complejidad
        linea.formula = complejidad.formula.lower() if complejidad else '0'
        linea.formula_valorizada = complejidad.formula.lower() if complejidad else '0'

        # reemplazamos en la fórmula los valores de cada complejidad
        for c in complejidades:
            linea.formula_valorizada = linea.formula_valorizada.replace('c{0}'.format(c.id), c.importe)

        # obtenermos el importe de la serie de estudios
        linea.importe = Decimal(eval_expr(linea.formula_valorizada))

        # obtenemos los movimientos de caja asociados
        linea.mov_caja = [mov
            for estudio in linea.estudios
            for mov     in estudio.movimientos_caja.filter(tipo_id__in=[TIPO_MOV_CAJA_HONORARIO_ANESTESISTA, TIPO_MOV_CAJA_COSEGURO])
        ]
        total_mov_caja = sum(mov.monto for mov in linea.mov_caja)

        linea_ara = None
        linea_no_ara = None
        if obra_social.se_presenta_por_ARA:
            linea_ara = linea
            if linea.mov_caja:  # si hay movimientos en cualquier estudio, la linea debe ir tanto en ARA como en NO ARA
                linea_ara = linea
                linea_no_ara = copy.deepcopy(linea)
                print "linea copiada {} {}".format(linea.fecha, linea.paciente)
        else:
            linea_no_ara = linea

        if linea_ara:
            linea_ara.alicuota_iva = 21.0  # solo se muestra al final del listado como total (valor)
            linea_ara.importe *= linea_ara.get_coeficiente_paciente_diferenciado()
 
            if linea.mov_caja:
                linea_ara.importe = linea_ara.importe - total_mov_caja

            pago.lineas_ARA.append(linea_ara)
            
        if linea_no_ara:
            # TODO: al importe que se calcule se le hace 100 - perc anest (lo que arriba era retencion, aca es a pagar)

            # TODO: iva va como oculto, en cada linea

            if obra_social.se_presenta_por_ARA: # (es duplicado de una linea_ara)
                linea_ara.importe = total_mov_caja
                linea_no_ara.alicuota_iva = 0  # ya esta incluido en el monto del mov. de caja
            else:
                if obra_social.is_particular_or_especial():
                    comprobante = linea.get_comprobante_particular()
                else:
                    comprobante = linea.get_comprobante_desde_facturacion()
                
                linea_no_ara.alicuota_iva = comprobante.gravado.porcentaje if comprobante and comprobante.tipo_comprobante.nombre != 'Liquidacion' else 0
                linea_no_ara.importe *= linea_no_ara.get_coeficiente_paciente_diferenciado()    


            pago.lineas_no_ARA.append(linea_no_ara)
            

    serializer = PagoAnestesistaVMSerializer(pago, context={'request': request})
    return JSONResponse(serializer.data)

