# -*- coding: utf-8 -*-

import ast
import operator as op
from anestesista.models import ComplejidadEstudio


def eval_expr(expr):
    
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


def get_complejidad_a_aplicar(estudios):
    """
    # generamos el patron de busqueda para la complejidad
    # (es una lista de codigos destudios ordenada y separada por coma)
    """

    estudios_id = ','.join([str(practica_id) for practica_id in sorted(set([estudio.practica.id for estudio in estudios]))])

    # obtenemos la complejidad de la serie de estudios
    # TODO: ver con MAriana. El azul compara que la lista estudios_id sea igual a la lista de la ComplejidadEstudio (misma posicion cada ID en el arreglo)
    complejidad = ComplejidadEstudio.objects.filter(estudios__contains=estudios_id).first()
    return complejidad

