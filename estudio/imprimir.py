
# -*- coding: utf-8
import os.path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import black
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

width, height = A4
margin_left = 13*mm
font_std = u'Helvetica'
font_bld = u'Helvetica-Bold'


def generar_informe(response, estudio):
    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle(u'Imprimir estudio de {}'.format(estudio.paciente))
    p.setLineWidth(0.5)

    _datos_estudio(p, estudio)

    _informe(p, estudio)

    if estudio.enlace_video:
        _pie(p, estudio)

    # Close the PDF object cleanly, and we're done.
    p.showPage()

    p.save()
    return response


def _datos_estudio(p, estudio):
    top = margin_left + 50*mm
    th = 9
    ld = 12

    p.saveState()

    # Practica (titulo)
    p.setFont(font_bld, 10)
    p.drawCentredString(width/2, height - top, estudio.practica.descripcion)

    t = p.beginText(1.5*margin_left, height - top - 25)

    # Fecha del estudio
    t.setFont(font_bld, th)
    t.textOut(u'Fecha del estudio.....: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio.fechaEstudio.strftime("%d/%m/%Y")))

    # Paciente
    t.setFont(font_bld, th)
    t.textOut(u'Paciente ....................: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    if estudio.paciente.get_edad():
        t.textLine(u'{} ({})'.format(str(estudio.paciente), str(estudio.paciente.get_edad())))
    else:
        t.textLine(u'{}'.format(str(estudio.paciente)))

    # Obra Social
    t.setFont(font_bld, th)
    t.textOut(u'Obra Social ...............: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio.obraSocial))

    # Nro de afiliado
    if estudio.paciente.nroAfiliado:
        t.setFont(font_bld, th)
        t.textOut(u'Nro de afiliado ..........: ')
        t.setFont(font_std, th)
        t.setLeading(ld)
        t.textLine(str(estudio.paciente.nroAfiliado))

    # Medico Solicitante
    t.setFont(font_bld, th)
    t.textOut(u'Medico Solicitante ...: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio.medicoSolicitante))

    # Motivo del estudio
    t.setFont(font_bld, th)
    t.textOut(u'Motivo del estudio ...: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio.motivoEstudio))


    p.drawText(t)
    p.restoreState()


def _informe(p, estudio):
    top = margin_left + 88*mm
    eh = 13*mm

    p.saveState()
    p.line(1.5*margin_left, height - top, 520 + margin_left, height - top)

    p.setFillColor(black)
    p.setFont(font_bld, 10)
    p.drawCentredString(width/2, height - top - eh + 10, u'INFORME')

    styles = getSampleStyleSheet()
    paragraph = Paragraph(estudio.informe.replace(u'\r', u'').replace(u'\n', u'<br/>'), styles["Normal"])

    w, h = paragraph.wrapOn(p, 170*mm, 150*mm)
    paragraph.drawOn(p, 1.5*margin_left, height - 265*mm + (150*mm - h))

    p.restoreState()


def _pie(p, estudio):
    th = 9

    p.saveState()
    p.line(1.5*margin_left, height - 660, 520 + margin_left, height - 660)

    filename = u'./savetheearth.jpg'
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    p.drawImage(fn, 1.5*margin_left, height - 810, width=30*mm, height=35*mm)

    p.setFont(font_std, 8)

    t = p.beginText(1.5*margin_left, height - 680)

    t.setFont(font_std, th)
    t.textLine(u'- El siguiente enlace web permitirá descargar el video del estudio a partir de las próximas 48hs de realizado.')
    p.drawText(t)

    t.setFont(font_std, th)
    t.textLine(u'- Recordar que sólo estará disponible para descarga durante los próximos 30 días de realizado el mismo.')
    p.drawText(t)

    t.setFont(font_std, th)
    t.textLine(u'- Coloque el siguiente enlace en la barra de direcciones de su explorador web, para proceder con la descarga del video.')
    p.drawText(t)

    p.setFont(font_std, 8)
    p.drawCentredString(width/2, height - 735, u'Al utilizar el link de descarga en vez de un DVD estas contribuyendo al cuidado')
    p.drawCentredString(width/2, height - 745, u'del medio ambiente')
    p.drawCentredString(width/2, height - 755, u'-------------------------------------------------------------------------------------------------------')

    p.setFont(font_std, 10)
    p.drawCentredString(width/2, height - 770, str(estudio.enlace_video))

    p.restoreState()
