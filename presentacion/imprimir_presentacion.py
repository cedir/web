from typing import Dict, List
from reportlab.platypus.tables import TableStyle
from rest_framework.response import Response
from itertools import chain

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

def generar_pdf_presentacion(response, presentacion):

    pdf = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        topMargin=600*mm,
        bottomMargin=10*mm,
        rightMargin=17*mm,
        leftMargin=17*mm
    )

    styles: StyleSheet1 = getSampleStyleSheet()
    styles["Normal"].fontSize = 14

    elements = encabezado(presentacion.obra_social, presentacion.fecha, styles) /
        + estudios(presentacion.estudios, styles)

    pdf.build(elements)
    return response