# -*- coding: utf-8 -*-
from django.shortcuts import render
from estudio.models import Estudio
from estudio.serializers import EstudioSerializer
from anestesista.models import ComplejidadEstudio, Complejidad, PagoAnestesistaVM, LineaPagoAnestesistaVM
from anestesista.serializers import AnestesistaSerializer, PagoAnestesistaVMSerializer, LineaPagoAnestesistaVMSerializer
from itertools import groupby

from models import Anestesista

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

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

# Create your views here.
def pago(request, id_anestesista, anio, mes):
    
    pago = PagoAnestesistaVM()

    pago.anestesista = Anestesista.objects.get(id=id_anestesista)
    pago.anio = anio
    pago.mes = mes

    # obtenemos los estudios por anestesista, año y mes    
    estudios = Estudio.objects.filter(anestesista_id=id_anestesista, fecha__year=anio, fecha__month=mes).order_by('fecha','paciente','obra_social')
    complejidades = Complejidad.objects.all()

    # agrupamos en paquetes fecha/paciente/obra_social
    grupos = groupby(estudios, lambda e: (e.fecha, e.paciente, e.obra_social))

    pago.lineas_ARA = []
    pago.lineas_no_ARA = []

    # por cada paquete
    for (fecha, paciente, obra_social), grupo in grupos:
        linea = LineaPagoAnestesistaVM()
        linea.fecha = fecha
        linea.paciente = paciente
        linea.obra_social = obra_social

        estudios = sorted(grupo, key=lambda estudio: estudio.practica.id)
           
        # obtenemos los movimientos de caja asociados
        linea.mov_caja = [mov
            for estudio in estudios
            for mov     in estudio.movimientos_caja.filter(tipo_id__in=[3,10])
            ]
        
        # generamos el patrón de búsqueda para la complejidad
        # (es una lista de codigos destudios ordenada y separada por coma)
        estudios_id = ','.join([str(id) for id in sorted(set([estudio.practica.id for estudio in estudios]))])

        # obtenemos la complejidad de la serie de estudios
        # TODO: revisar contains vs igual y get
        complejidad = ComplejidadEstudio.objects.filter(estudios__contains=estudios_id).first()

        # obtenemos la fórmula de cálculo de la complejidad
        linea.formula = complejidad.formula.lower() if complejidad else '0'
        linea.formula_valorizada = complejidad.formula.lower() if complejidad else '0'

        # reemplazamos en la fórmula los valores de cada complejidad
        for c in complejidades:
            linea.formula_valorizada = linea.formula_valorizada.replace('c{0}'.format(c.id), c.importe)
        
        # obtenermos el importe de la serie de estudios
        linea.importe = eval_expr(linea.formula_valorizada)
        linea.alicuota_iva = 21.0

        # determinamos si el paciente tiene una edad diferenciada
        linea.es_paciente_diferenciado = paciente.edad >= 70 or paciente.edad < 12

        if linea.es_paciente_diferenciado:
            linea.importe *= 1.3

        linea.estudios = estudios
        
        if obra_social.se_presenta_por_ARA:
            pago.lineas_ARA.append(linea)
        else:
            pago.lineas_no_ARA.append(linea)

    serializer = PagoAnestesistaVMSerializer(pago, context={'request': request})
    return JSONResponse(serializer.data)