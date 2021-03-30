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

    pdf.build(elements)
    return response

def pdf_encabezado(fecha: str, monto_acumulado: int) -> Table:
    encabezado = [[Paragraph('Informe movimientos de caja', styles['Heading3']), '', f'Dia: {fecha}      Monto acumulado: {monto_acumulado}']]
    return [Table(encabezado)]