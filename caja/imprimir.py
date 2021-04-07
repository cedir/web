from django.http import HttpResponse
from caja.serializers import MovimientoCajaFullSerializer
from typing import Union, List

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, Paragraph

styles = getSampleStyleSheet()

def generar_pdf_caja(response: HttpResponse, movimientos: MovimientoCajaFullSerializer, fecha: str) -> HttpResponse:

    pdf = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
    )

    elements = pdf_encabezado(fecha, movimientos[0]['monto_acumulado'])
    elements += pdf_tabla(movimientos)

    pdf.build(elements)
    return response

def pdf_encabezado(fecha: str, monto_acumulado: int) -> Table:
    encabezado = [[paragraph('Informe movimientos de caja', 'Heading3'),
                   '', f'Dia: {fecha}      Monto acumulado: {monto_acumulado}']]
    return [Table(encabezado)]

def pdf_tabla(movimientos: MovimientoCajaFullSerializer):
    return [Table(pdf_tabla_encabezado() + pdf_tabla_body(movimientos))]

def pdf_tabla_encabezado():
    return [[
        paragraph('Usuario'),
        paragraph('Tipo de mov.'),
        paragraph('Paciente'),
        paragraph('Obra Social'),
        paragraph('Médico'),
        paragraph('Práctica'),
        paragraph('Detalle'),
        paragraph('Monto'),
        paragraph('Monto ac.'),
    ]]


def pdf_tabla_body(movimientos: MovimientoCajaFullSerializer) -> List[List[Paragraph]]:
    return [[
        paragraph('-'),
        paragraph(movimiento['tipo']),
        paragraph(movimiento['paciente']),
        paragraph(movimiento['obra_social']),
        paragraph(movimiento['medico']),
        paragraph(movimiento['practica']),
        paragraph(movimiento['concepto']),
        paragraph(movimiento['monto']),
        paragraph(movimiento['monto_acumulado'])] for movimiento in movimientos
    ]

def paragraph(text: Union[str, int], estilo: str = 'Normal') -> Paragraph:
    return Paragraph(text, styles[estilo])