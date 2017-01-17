# -*- coding: utf-8 -*-
from django.shortcuts import render
from estudio.models import Estudio
from estudio.serializers import EstudioSerializer
from anestesista.models import ComplejidadEstudio, Complejidad
from itertools import groupby

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

    # obtenemos los estudios por anestesista, año y mes    
    estudios = Estudio.objects.filter(anestesista_id=id_anestesista, fecha__year=anio, fecha__month=mes).order_by('fecha','paciente','obra_social')
    complejidades = Complejidad.objects.all()

    # agrupamos en paquetes fecha/paciente/obra_social
    grupos = groupby(estudios, lambda e: (e.fecha, e.paciente.id, e.obra_social.id))

    # por cada paquete
    for clave, grupo in grupos:
        estudios = sorted(grupo, key=lambda estudio: estudio.practica.id)
        # obtenemos los movimientos de caja asociados
        mov_caja = [mov
            for estudio in estudios
            for mov     in estudio.movimientos_caja.filter(tipo_id__in=[3,10])
            ]

        estudios_id = ','.join([str(id) for id in sorted(set([estudio.practica.id for estudio in estudios]))])

        complejidad = ComplejidadEstudio.objects.filter(estudios__contains=estudios_id).first()

        formula = complejidad.formula.lower() if complejidad else '0'

        for c in complejidades:
            formula = formula.replace('c{0}'.format(c.id), c.importe)

        importeIAPOS = eval_expr(formula)

        print (clave, estudios_id, formula, importeIAPOS)

    return JSONResponse([])