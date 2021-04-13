from django.http import HttpResponse
from caja.serializers import MovimientoCajaImprimirSerializer as MovimientosSerializer
from typing import Union, List, Optional
from datetime import datetime
from decimal import Decimal

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, Paragraph, TableStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from settings import GOTHIC_FONT_PATH, GOTHIC_BOLD_FONT_PATH

GRIS_CLARO = 0xE0E0E0
GRIS_OSCURO = 0xBDBBBC

LARGOS_CABECERA = [100*mm, 75*mm, 103*mm]
MARGINS = { 'top': 10*mm, 'bottom': 10*mm }

COLUMNAS = (('Usuario', 17*mm, 'usuario'), ('Tipo de mov.', 27*mm, 'tipo'),
            ('Paciente', 33*mm, 'paciente'), ('Obra Social', 33*mm, 'obra_social'),
            ('Médico', 33*mm, 'medico'), ('Práctica', 33*mm, 'practica'),
            ('Detalle', 59*mm, 'concepto'), ('Monto', 19*mm, 'monto'),
            ('Monto ac.', 23*mm, 'monto_acumulado'))  #En cada entrada posee (nombre_columna, tamaño, key)


def paragraph(text: Union[str, int], estilo: str = 'Normal') -> Paragraph:
    return Paragraph(text, styles[estilo])

def setUpStyles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT, fontSize=12, parent=styles['Normal']))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=12, parent=styles['Normal']))
    
    try:
        pdfmetrics.registerFont(TTFont('Gothic', GOTHIC_FONT_PATH))
        pdfmetrics.registerFont(TTFont('Gothic-Bold', GOTHIC_BOLD_FONT_PATH))
    
        styles['Normal'].fontName='Gothic'
        styles['Normal'].fontSize=10
        styles['Heading3'].fontName='Gothic-Bold'
        styles['Heading3'].fontSize = 12
    
    except Exception:
        pass

    return styles
    
styles = setUpStyles()

def generar_pdf_caja(response: HttpResponse, movimientos: MovimientosSerializer, fecha: Optional[datetime], monto_acumulado: Decimal) -> HttpResponse:
    pdf = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        title='Movimientos de caja {0}'.format(fecha),
        topMargin=MARGINS['top'],
        bottomMargin=MARGINS['bottom'],
    )

    elements = pdf_encabezado(fecha, monto_acumulado)
    elements += pdf_tabla(movimientos)

    pdf.build(elements)
    return response


def pdf_encabezado(fecha: Optional[datetime], monto_acumulado: int) -> List[Table]:
    fecha_str = fecha.strftime('%A, %d de %B de %Y') if fecha else ''
    return [Table([[
        paragraph('INFORME DE MOVIMIENTOS DE CAJA', 'Heading3'),
        paragraph(fecha_str, 'Center'),
        paragraph(f'Monto acumulado hasta la fecha: {monto_acumulado}', 'Right')
        ]],
        colWidths=LARGOS_CABECERA,
    )]


def pdf_tabla(movimientos: MovimientosSerializer) -> List[Table]:
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


def pdf_tabla_encabezado() -> List[List[Paragraph]]:
    return [[paragraph(columna[0]) for columna in COLUMNAS]]


def pdf_tabla_body(movimientos: MovimientosSerializer) -> List[List[Paragraph]]:
    return [
        [paragraph(movimiento[key[2]]) for key in COLUMNAS]
        for movimiento in movimientos
    ]
