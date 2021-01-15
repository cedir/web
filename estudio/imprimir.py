# -*- coding: utf-8
import os.path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate

styles = getSampleStyleSheet()

font_std = styles["Normal"]
font_std.fontName = 'Helvetica'
font_std.alignment = TA_JUSTIFY
font_std.fontSize = 10


def generar_informe(response, estudio):
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=55*mm,
        bottomMargin=65*mm if estudio.enlace_video else 25*mm,
        rightMargin=17*mm,
        leftMargin=17*mm
    )

    elements = []

    _datos_estudio(elements, estudio)
    _informe(elements, estudio)

    doc.build(elements, onFirstPage=_draw_firstpage_frame(estudio), onLaterPages=_draw_firstpage_frame(estudio, False))
    return response


def _datos_estudio(elements, estudio):
    # Practica (titulo)
    elements.append(Paragraph('<para align="CENTER" spaceAfter="15"><b>{}</b></para>'.format(estudio.practica.descripcion), font_std))

    # reducimos momentáneamente el tamaño de la fuente
    font_std.fontSize = 9

    # fecha estudio
    fecha = '<b>Fecha del estudio.....:</b> {0}'.format(str(estudio.fecha.strftime("%d/%m/%Y")))
    elements.append(Paragraph(fecha, font_std))

    # Paciente
    edad = estudio.paciente.get_edad()
    if edad:
        paciente = '<b>Paciente ....................:</b> {} ({} años)'.format(estudio.paciente, edad)
    else:
        paciente = '<b>Paciente ....................:</b> {}'.format(estudio.paciente)

    elements.append(Paragraph(paciente, font_std))

    # Obra Social
    obra_social = '<b>Obra Social ...............:</b> {0}'.format(estudio.obra_social.nombre)
    elements.append(Paragraph(obra_social, font_std))

    # Nro de afiliado
    if estudio.paciente.nroAfiliado:
        nro_afiliado = '<b>Nro de afiliado ..........:</b> {0}'.format(str(estudio.paciente.nroAfiliado))
        elements.append(Paragraph(nro_afiliado, font_std))

    # Medico Solicitante
    medico_sol = '<b>Medico Solicitante ...:</b> {0}'.format(str(estudio.medico_solicitante))
    elements.append(Paragraph(medico_sol, font_std))

    # Motivo del estudio
    motivo = '<para spaceAfter="43" ><b>Motivo del estudio ...:</b> {0}</para>'.format(estudio.motivo)
    elements.append(Paragraph(motivo, font_std))

    # restauramos el tamaño de la fuente
    font_std.fontSize = 10


def _informe(elements, estudio):
    elements.append(Paragraph('<para alignment="CENTER" spaceAfter="10"><b>INFORME</b></para>', font_std))
    elements.append(Paragraph(estudio.informe.replace('\r', '').replace('\n', '<br/>'), font_std))


def _draw_firstpage_frame(estudio, imprimeLinea=True):
    def _nada(canvas, doc):
        # calculamos algunas dimensiones
        width, height = doc.pagesize
        linea_superior = height - doc.topMargin - 46*mm

        canvas.saveState()

        # dibujamos las dos líneas
        if imprimeLinea:
            canvas.line(doc.leftMargin, linea_superior, width - doc.rightMargin, linea_superior)

        canvas.restoreState()

    # armamos un clausura porque necesitamos acceder a información del estudio
    def _pie(canvas, doc):
        # calculamos algunas dimensiones
        width, height = doc.pagesize
        linea_superior = height - doc.topMargin - 46*mm
        linea_inferior = doc.bottomMargin

        canvas.saveState()

        # dibujamos las dos líneas
        if imprimeLinea:
            canvas.line(doc.leftMargin, linea_superior, width - doc.rightMargin, linea_superior)

        canvas.line(doc.leftMargin, linea_inferior, width - doc.rightMargin, linea_inferior)

        # dibujamos la imágen
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), './savetheearth.jpg')
        canvas.drawImage(
            filename,
            1.2 * doc.leftMargin,
            height - 810,
            width=30 * mm,
            height=35 * mm
            )

        # dibujamos las leyendas
        t = canvas.beginText(1.2 * doc.leftMargin, height - 680)

        t.setFont(font_std.fontName, font_std.fontSize - 1)
        t.textLine('- El siguiente enlace web permitirá descargar el video del estudio a partir '
                   'de las próximas 48hs de realizado.')

        t.textLine('- Recordar que sólo estará disponible para descarga durante los próximos 30 días '
                   'de realizado el mismo.')

        t.textLine('- Coloque el siguiente enlace en la barra de direcciones de su explorador web, '
                   'para proceder con la descarga del video.')

        canvas.drawText(t)

        canvas.setFont(font_std.fontName, font_std.fontSize - 2)
        canvas.drawCentredString(
            width / 2,
            height - 735,
            'Al utilizar el link de descarga en vez de un DVD estas contribuyendo al cuidado'
            )

        canvas.drawCentredString(
            width / 2,
            height - 745,
            'del medio ambiente'
            )

        canvas.drawCentredString(
            width / 2,
            height - 755,
            '-------------------------------------------------------------------------------------------------------'
            )

        canvas.setFont(font_std.fontName, 10)
        canvas.drawCentredString(
            width / 2,
            height - 770,
            'http://www.cedir.com.ar/video/{0}'.format(str(estudio.public_id))
            )

        canvas.restoreState()
    if estudio.enlace_video:
        return _pie
    else:
        return _nada
