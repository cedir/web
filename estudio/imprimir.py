
# -*- coding: utf-8
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import black,white, Color
from reportlab.graphics.barcode.common import I2of5
from reportlab.platypus import Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from textwrap import wrap

from datetime import timedelta

width, height = A4
margin = 6*mm
font_std = 'Helvetica'
font_bld = 'Helvetica-Bold'





def generar_informe(response, estudio):
    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle("aasdasdsad")

    p.setLineWidth(0.5)

    # Escribe encabezado
    #encabezado(p, copia)

    _informe(p, estudio)

    # Close the PDF object cleanly, and we're done.
    p.showPage()

    p.save()
    return response

def _informe(p, estudio):
    top = margin + 10*mm
    ew = (width - 2*margin) / 2
    eh = 45*mm
    th = 9
    ld = 25

    p.saveState()
    p.rect(margin, height - top - eh , ew, eh, stroke=1, fill=0)

    t = p.beginText(1.5*margin, height - top - 25)

    # Nombre Grande
    t.setFont(font_bld, 16)
    #t.textLines(u'\n'.join("asdasd", 25)))

    # Nombre
    t.setFont(font_bld, th)
    t.textOut(u'Razón Social: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio))

    # Domicilio
    t.setFont(font_bld, th)
    t.textOut(u'Domicilio Comercial: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio))

    # Condición IVA
    t.setFont(font_bld, th)
    t.textOut(u'Condición frente al IVA: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio))

    p.drawText(t)

    p.restoreState()

