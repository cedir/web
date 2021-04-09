from django.http import HttpResponse
from caja.serializers import MovimientoCajaImprimirSerializer
from typing import Union, List

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, Paragraph, TableStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors

styles = getSampleStyleSheet()
MARGINS = {
    'top': 10*mm,
    'bottom': 10*mm,
}
COLS_WIDTH = [17*mm, 26*mm] + [33*mm]*4 + [62*mm] + [20*mm, 20*mm]

def generar_pdf_caja(response: HttpResponse, movimientos: MovimientoCajaImprimirSerializer, fecha: str) -> HttpResponse:
    pdf = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        title=f'movimientos del dia {fecha}',
        topMargin=MARGINS['top'],
        bottomMargin=MARGINS['bottom'],
    )

    elements = pdf_encabezado(fecha, movimientos[0]['monto_acumulado'])
    elements += pdf_tabla(movimientos)

    pdf.build(elements)
    return response

def pdf_encabezado(fecha: str, monto_acumulado: int) -> Table:
    encabezado = [[paragraph('Informe movimientos de caja', 'Heading3'),
                   '', f'Dia: {fecha}      Monto acumulado: {monto_acumulado}']]
    return [Table(encabezado)]

def pdf_tabla(movimientos: MovimientoCajaImprimirSerializer):
    table_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')])
    table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0xBDBBBC))

    for i in range(1, len(movimientos)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor(0xE0E0E0))

    table = Table(pdf_tabla_encabezado() + pdf_tabla_body(movimientos), colWidths=COLS_WIDTH)

    table.setStyle(table_style)

    return [table]

def pdf_tabla_encabezado():
    return [[paragraph(key) for key in ('Usuario', 'Tipo de mov.', 'Paciente', 'Obra Social', 'Médico', 'Práctica', 'Detalle', 'Monto', 'Monto ac.')]]

def pdf_tabla_body(movimientos: MovimientoCajaImprimirSerializer) -> List[List[Paragraph]]:
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