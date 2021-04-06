from django.http import HttpResponse
from caja.serializers import MovimientoCajaFullSerializer

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
    encabezado = [[Paragraph('Informe movimientos de caja', styles['Heading3']),
                   '', f'Dia: {fecha}      Monto acumulado: {monto_acumulado}']]
    return [Table(encabezado)]

def pdf_tabla(movimientos: MovimientoCajaFullSerializer):
    return [Table(pdf_tabla_encabezado() + pdf_tabla_body(movimientos))]

def pdf_tabla_encabezado():
    return [[
        Paragraph('Usuario', styles['Normal']),
        Paragraph('Tipo de mov.', styles['Normal']),
        Paragraph('Paciente', styles['Normal']),
        Paragraph('Obra Social', styles['Normal']),
        Paragraph('Médico', styles['Normal']),
        Paragraph('Práctica', styles['Normal']),
        Paragraph('Detalle', styles['Normal']),
        Paragraph('Monto', styles['Normal']),
        Paragraph('Monto ac.', styles['Normal']),
    ]]


def pdf_tabla_body(movimientos: MovimientoCajaFullSerializer):
    return [[
        Paragraph('-', styles['Normal']),
        Paragraph(movimiento['tipo'], styles['Normal']),
        Paragraph(movimiento['paciente'], styles['Normal']),
        Paragraph(movimiento['obra_social'], styles['Normal']),
        Paragraph(movimiento['medico'], styles['Normal']),
        Paragraph(movimiento['practica'], styles['Normal']),
        Paragraph(movimiento['concepto'], styles['Normal']),
        Paragraph(movimiento['monto'], styles['Normal']),
        Paragraph(movimiento['monto_acumulado'], styles['Normal'])] for movimiento in movimientos
    ]
