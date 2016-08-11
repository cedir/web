
# -*- coding: utf-8
import os.path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate

width, height = A4
margin_left = 13*mm
styles = getSampleStyleSheet()

font_std = styles["Normal"]
font_std.fontName = 'Helvetica'
font_std.alignment = TA_JUSTIFY
font_std.fontSize = 10


def generar_informe_nuevo(response, estudio):
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

    _datos_estudio(elements, estudio)
    _informe(elements, estudio)

    doc.build(elements, onFirstPage=_drawFirstPageFrame(estudio))
    return response


def _datos_estudio(elements, estudio):
    # Practica (titulo)
    elements.append(Paragraph(u'<para align="CENTER" spaceAfter="15"><b>{}</b></para>'.format(estudio.practica.descripcion), font_std))

    # reducimos momentáneamente el tamaño de la fuente
    font_std.fontSize = 9

    # fecha estudio
    fecha = u'<b>Fecha del estudio.....:</b> {0}'.format(unicode(estudio.fechaEstudio.strftime("%d/%m/%Y")))
    elements.append(Paragraph(fecha, font_std))

    # Paciente
    edad = estudio.paciente.get_edad()
    if edad:
        paciente = u'<b>Paciente ....................:</b> {} ({} años)'.format(estudio.paciente, edad)
    else:
        paciente = u'<b>Paciente ....................:</b> {}'.format(estudio.paciente, edad)

    elements.append(Paragraph(paciente, font_std))

    # Obra Social
    obra_social = u'<b>Obra Social ...............:</b> {0}'.format(estudio.obraSocial.nombre)
    elements.append(Paragraph(obra_social, font_std))

    # Nro de afiliado
    if estudio.paciente.nroAfiliado:
        nro_afiliado = u'<b>Nro de afiliado ..........:</b> {0}'.format(unicode(estudio.paciente.nroAfiliado))
        elements.append(Paragraph(nro_afiliado, font_std))

    # Medico Solicitante
    medico_sol = u'<b>Medico Solicitante ...:</b> {0}'.format(unicode(estudio.medicoSolicitante))
    elements.append(Paragraph(medico_sol, font_std))

    # Motivo del estudio
    motivo = u'<para spaceAfter="43" ><b>Motivo del estudio ...:</b> {0}</para>'.format(estudio.motivoEstudio)
    elements.append(Paragraph(motivo, font_std))

    font_std.fontSize = 10


def _informe(elements, estudio):

    # p.line(1.5*margin_left, height - top, 520 + margin_left, height - top)
    elements.append(Paragraph(u'<para alignment="CENTER" spaceAfter="10"><b>INFORME</b></para>', font_std))
    elements.append(Paragraph(estudio.informe.replace(u'\r', u'').replace(u'\n', u'<br/>'), font_std))

def _drawFirstPageFrame(estudio):
    def _pie(p, doc):
        th = 9
        p.saveState()

        p.line(1.5*margin_left, height - 285, 520 + margin_left, height - 285)

        p.line(1.5*margin_left, height - 660, 520 + margin_left, height - 660)

        filename = u'./savetheearth.jpg'
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        p.drawImage(fn, 1.5*margin_left, height - 810, width=30*mm, height=35*mm)

        p.setFont(font_std.fontName, 8)

        t = p.beginText(1.5*margin_left, height - 680)

        t.setFont(font_std.fontName, th)
        t.textLine(u'- El siguiente enlace web permitirá descargar el video del estudio a partir de las próximas 48hs de realizado.')
        p.drawText(t)

        t.setFont(font_std.fontName, th)
        t.textLine(u'- Recordar que sólo estará disponible para descarga durante los próximos 30 días de realizado el mismo.')
        p.drawText(t)

        t.setFont(font_std.fontName, th)
        t.textLine(u'- Coloque el siguiente enlace en la barra de direcciones de su explorador web, para proceder con la descarga del video.')
        p.drawText(t)

        p.setFont(font_std.fontName, 8)
        p.drawCentredString(width/2, height - 735, u'Al utilizar el link de descarga en vez de un DVD estas contribuyendo al cuidado')
        p.drawCentredString(width/2, height - 745, u'del medio ambiente')
        p.drawCentredString(width/2, height - 755, u'-------------------------------------------------------------------------------------------------------')

        p.setFont(font_std.fontName, 10)
        p.drawCentredString(width/2, height - 770, u'http://www.cedirsalud.com.ar/video/{}'.format(str(estudio.public_id)))

        p.restoreState()

    return _pie
