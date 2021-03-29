from django.http import HttpResponse
from caja.serializers import MovimientoCajaFullSerializer

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, KeepTogether

styles = getSampleStyleSheet()

def generar_pdf_caja(response: HttpResponse, movimientos: MovimientoCajaFullSerializer):

    pdf = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
    )
    pdf.build([Paragraph('Prueba', styles['Normal'])])
    return response
