from typing import List
from rest_framework.response import Response

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black,white, Color

from medico.models import PagoMedico


styles = getSampleStyleSheet()

font_std = styles["Normal"]
font_std.fontName = 'Helvetica'
font_std.alignment = TA_JUSTIFY
font_std.fontSize = 10

def generar_pdf_detalle_pago(response: Response, pago: PagoMedico) -> Response:
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=55*mm,
        bottomMargin=65*mm,
        rightMargin=17*mm,
        leftMargin=17*mm
    )

    elements = []

    _datos_pago(elements, pago)
    _detalle(elements, pago)

    doc.build(elements)
    return response

def _datos_pago(elements: List[Flowable], pago: PagoMedico) -> None:
    pass

def _detalle(elements: List[Flowable], pago: PagoMedico) -> None:
    pass