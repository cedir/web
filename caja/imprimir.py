from django.http import HttpResponse
from caja.serializers import MovimientoCajaImprimirSerializer
from typing import Union, List

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, Paragraph, TableStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors


MARGINS = {
    'top': 10*mm,
    'bottom': 10*mm,
}
COLUMNAS = (('Usuario', 17*mm), ('Tipo de mov.', 26*mm), ('Paciente', 33*mm),
            ('Obra Social', 33*mm), ('Médico', 33*mm), ('Práctica', 33*mm),
            ('Detalle', 62*mm), ('Monto', 20*mm), ('Monto ac.', 20*mm))

GRIS_CLARO = 0xE0E0E0
GRIS_OSCURO = 0xBDBBBC

styles = getSampleStyleSheet()

def paragraph(text: Union[str, int], estilo: str = 'Normal') -> Paragraph:
    return Paragraph(text, styles[estilo])


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
    table_style = TableStyle(
        [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(GRIS_OSCURO))] +       # La fila con los nombres de las columnas esta con fondo gris oscuro
        [('BACKGROUND', (0, i), (-1, i), colors.HexColor(GRIS_CLARO))           # Las filas pares tienen fondo gris claro
         for i in range(2, len(movimientos), 2)]
    )

    return [Table(
        pdf_tabla_encabezado() + pdf_tabla_body(movimientos),
        colWidths=[columna[1] for columna in COLUMNAS],
        style=table_style,
    )]


def pdf_tabla_encabezado():
    return [[paragraph(columna[0]) for columna in COLUMNAS]]


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
