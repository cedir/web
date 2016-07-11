
# -*- coding: utf-8
import os.path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import black,white, Color
from reportlab.graphics.barcode.common import I2of5
from reportlab.platypus import Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.encoding import smart_str, smart_unicode

from textwrap import wrap

from datetime import timedelta

width, height = A4
margin_left = 13*mm
font_std = 'Helvetica'
font_bld = 'Helvetica-Bold'


def generar_informe(response, estudio):
    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle("Imprimir estudio de {}".format(estudio.paciente))
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
    ew = (width - 2*margin_left) / 2
    eh = 45*mm
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
    t.textLine(str(estudio.fechaEstudio))

    # Paciente
    t.setFont(font_bld, th)
    t.textOut(u'Paciente ....................: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(u'{} ({})'.format(str(estudio.paciente), str(estudio.paciente.get_edad())))

    # Obra Social
    t.setFont(font_bld, th)
    t.textOut(u'Obra Social ...............: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(str(estudio.obraSocial))

    # Nro de afiliado
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
    ew = 16*mm
    eh = 13*mm
    #th = 9
    #ld = 25

    p.saveState()
    p.line(1.5*margin_left, height - top, 520 + margin_left, height - top)

    p.setFillColor(black)
    p.setFont(font_bld, 10)
    p.drawCentredString(width/2, height - top - eh + 10, "INFORME")

    styles = getSampleStyleSheet()
    paragraph = Paragraph(estudio.informe.replace(u'\r', u'').replace(u'\n', u'<br/>'), styles["Normal"])

    #paragraph.wrapOn(p, 180*mm, 100*mm)
    #paragraph.drawOn(p, 1.5*margin_left, height - 200*mm)

    #paragraph.wrapOn(p, 100*mm, 100*mm)
    #paragraph.drawOn(p, *coord(20, 48, mm))

    from reportlab.platypus.flowables import KeepInFrame   # ejemplo en http://two.pairlist.net/pipermail/reportlab-users/2009-April/008180.html

    f = KeepInFrame(180*mm, 100*mm,[paragraph],mode='shrink')
    w,h=f.wrapOn(p,100*mm,100*mm)
    f.drawOn(p,1.5*margin_left, height - 200*mm)

    #p.drawText(t)
    #p.restoreState()


#def coord(x, y, unit=1):
#        """
#        # http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
#        Helper class to help position flowables in Canvas objects
#        """
#        x, y = x * unit, height -  y * unit
#        return x, y  


def _pie(p, estudio):
    top = margin_left + 200*mm
    ew = width - 2*margin_left
    eh = 7*mm
    th = 9
    ld = 25

    p.saveState()
    p.line(1.5*margin_left, height - 660, 520 + margin_left, height - 660)

    filename = './savetheearth.jpg'
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'savetheearth.jpg')
    p.drawImage(fn, 1.5*margin_left, height - 660)


    p.setFont(font_std, 8)

    t = p.beginText(1.5*margin_left, height - 680)

    t.setFont(font_bld, th)
    #t.setLeading(ld)
    t.textLine(u'- El siguiente enlace web permitirá descargar el video del estudio a partir de las próximas 48hs de realizado.')
    p.drawText(t)

    t.setFont(font_bld, th)
    #t.setLeading(ld)
    t.textLine(u'- Recordar que sólo estará disponible para descarga durante los próximos 30 días de realizado el mismo.')
    p.drawText(t)

    t.setFont(font_bld, th)
    #t.setLeading(ld)
    t.textLine(u'- Coloque el siguiente enlace en la barra de direcciones de su explorador web, para proceder con la descarga del video.')
    p.drawText(t)

    p.setFont(font_std, 11)
    p.drawCentredString(width/2, height - 800, str(estudio.enlace_video))

    p.restoreState()
