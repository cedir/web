# -*- coding: utf-8
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import black,white, Color
from reportlab.graphics.barcode.common import I2of5
from reportlab.platypus import Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from comprobante.models import *

from textwrap import wrap

from datetime import timedelta

width, height = A4
margin = 6*mm
font_std = 'Helvetica'
font_bld = 'Helvetica-Bold'
max_char = 24

mensajes = {
    'mensaje_leyenda_honorarios': u'Este comprobante contiene honorarios por cuenta y órden de médicos.',
    'mensaje_legal_factura_electronica': ('Pasados 30 días corridos de recibida sin \n'
                        'haberse producido el rechazo total, aceptación\n'
                        'o pago de esta FACTURA DE CREDITO\n'
                        'ELECTRONICA, se considerará que la misma\n'
                        'constituye título ejecutivo, en los términos del\n'
                        'artículo 523 del Código Procesal, Civil y\n'
                        'Comercial de la Nación y concordantes.\n'
                        'La aceptación expresa o tácita implicará la\n'
                        'plena conformidad para la transferencia de la\n'
                        'información contenida en el documento a\n'
                        'terceros, en caso de optar por su cesión,\n'
                        'transmisión o negociación.')
}

# TODO pasar a base de datos
responsables = {
    'cedir': {
        'CBU': '0150506102000109564632',
        'CUIT': '30709300152',
        'nombre': u'C.E.DI.R Centro de Endoscopia Digestiva',
        'razon': u'C.E.D.I.R Sociedad Colectiva',
        'direccion': u'Bv. Oroño 1564. - Rosario Sud, Santa Fe.',
        'condicion_iva': u'IVA Responsable Inscripto',
        'condicion_ib': '021-335420-4',
        'inicio_actividades': '30/06/2005',
    },
    'brunetti': {
        'CUIT': '20118070659',
        'nombre': u'Brunetti Jose Edgar Alberto',
        'razon': u'Brunetti Jose Edgar Alberto',
        'direccion': u'Bv. Oroño 1564. - Rosario Sud, Santa Fe.',
        'condicion_iva': u'IVA Responsable Inscripto',
        'condicion_ib': 'Excento',
        'inicio_actividades': '02/01/1992',
        'mensaje': u'"MÉDICO GASTROENTERÓLOGO Mat. Nro. 9314"',
    }
}

def digito_verificador_modulo10(numero):
    "Rutina para el cálculo del dígito verificador 'módulo 10'"
    codigo = str(numero)
    # Ver RG 1702 AFIP
    # Etapa 1: comenzar desde la izquierda, sumar todos los caracteres ubicados en las posiciones impares.
    etapa1 = sum([int(c) for i, c in enumerate(codigo) if not i % 2])
    # Etapa 2: multiplicar la suma obtenida en la etapa 1 por el número 3
    etapa2 = etapa1 * 3
    # Etapa 3: comenzar desde la izquierda, sumar todos los caracteres que están ubicados en las posiciones pares.
    etapa3 = sum([int(c) for i, c in enumerate(codigo) if i % 2])
    # Etapa 4: sumar los resultados obtenidos en las etapas 2 y 3.
    etapa4 = etapa2 + etapa3
    # Etapa 5: buscar el menor número que sumado al resultado obtenido en la etapa 4 dé un número múltiplo de 10.
    # Este será el valor del dígito verificador del módulo 10.
    digito = 10 - (etapa4 % 10)
    if digito == 10:
        digito = 0
    return numero*10 + digito


def codigo_barra_i25(canvas, cabecera):
        altura = 12 * mm
        trazoFino = 0.24 * mm # Tamanho correto aproximado
        x, y = 1.5*margin, 23*mm

        num = digito_verificador_modulo10(cabecera['codigo_barras'])

        bc = I2of5(num,
                   barWidth=trazoFino,
                   ratio=2.5,
                   barHeight=altura,
                   bearers=0,
                   quiet=0,
                   checksum=0)

        bc.drawOn(canvas, x, y)
        canvas.saveState()
        canvas.setFont(font_std, 8)
        canvas.drawCentredString(x + bc.width/2, y - 3*mm, str(num))
        canvas.restoreState()


def cae_y_fecha (p, cabecera):
    x, y = width - 40*mm, 30*mm
    p.saveState()
    p.setFont(font_bld, 10)
    p.drawRightString(x, y, 'CAE:')
    p.drawRightString(x, y - 10, 'Fecha de Vto. de CAE:')
    p.setFont(font_std, 10)
    p.drawString(x + 10, y, cabecera['CAE'])
    p.drawString(x + 10, y - 10, cabecera['CAE_vencimiento'])
    p.restoreState()


def encabezado(p, tipo):
    top = margin
    ew = width - 2*margin
    eh = 10*mm
    p.saveState()
    p.rect((width - ew)/2, height - top - eh , ew, eh, stroke=1, fill=0)
    p.setFont(font_bld, 14)
    p.drawCentredString(width/2, height - top - eh/2 - 6, tipo.upper())
    p.restoreState()


def zona_izquierda(p, responsable):
    top = margin + 10*mm
    ew = (width - 2*margin) / 2
    eh = 50*mm
    th = 9
    ld = 25

    p.saveState()
    p.rect(margin, height - top - eh , ew, eh, stroke=1, fill=0)

    t = p.beginText(1.5*margin, height - top - 25)

    # Nombre Grande
    t.setFont(font_bld, 16)
    t.textLines(u'\n'.join(wrap(responsable['nombre'].upper(), 25)))

    # Nombre
    t.setFont(font_bld, th)
    t.textOut(u'Razón Social: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(responsable['razon'])

    # Domicilio
    t.setFont(font_bld, th)
    t.textOut(u'Domicilio Comercial: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(responsable['direccion'])

    # Condición IVA
    t.setFont(font_bld, th)
    t.textOut(u'Condición frente al IVA: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(responsable['condicion_iva'])

    p.drawText(t)

    p.restoreState()


def zona_derecha(p, cabecera, responsable):
    top = margin + 10*mm
    ew = (width - 2*margin) / 2
    eh = 50*mm
    th = 9
    ld = 28
    fc = 0.45
    sp = 20

    p.saveState()
    p.rect(width - ew - margin, height - top - eh , ew, eh, stroke=1, fill=0)

    t = p.beginText(width - ew - margin + 17*mm, height - top - 25)

    # Descripción factura
    t.setFont(font_bld, 16)

    for s in cabecera['tipo'].split('\n'):
        t.textLine(s.upper())

    # Punto y Numero
    t.setFont(font_bld, th)
    t.setLeading(fc*ld)
    t.textLine(u'Punto de Venta: {punto_venta:04d}    Comp.Nro: {numero:08d}'.format(**cabecera))

    # Fecha de emisión
    t.textOut(u'Fecha de Emisión: ')
    t.setFont(font_std, th)
    t.setLeading(sp)
    t.textLine(cabecera['fecha'])

    # CBU
    if cabecera['id_tipo_comprobante'] == ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA:
        t.setFont(font_bld, th)
        t.textOut(u'CBU: ')
        t.setFont(font_std, th)
        t.setLeading(fc*ld)
        t.textLine(responsable['CBU'])

    # CUIT
    t.setFont(font_bld, th)
    t.textOut(u'CUIT: ')
    t.setFont(font_std, th)
    t.setLeading(fc*ld)
    t.textLine(responsable['CUIT'])

    # Ingresos Brutos
    t.setFont(font_bld, th)
    t.textOut(u'Ingresos Brutos: ')
    t.setFont(font_std, th)
    t.setLeading(fc*ld)
    t.textLine(responsable['condicion_ib'])

    # Inicio de actividades
    t.setFont(font_bld, th)
    t.textOut(u'Inicio de Actividades: ')
    t.setFont(font_std, th)
    t.setLeading(fc*ld)
    t.textLine(responsable['inicio_actividades'])

    p.drawText(t)
    p.restoreState()


def zona_central(p, cabecera):
    top = margin + 10*mm
    ew = 16*mm
    eh = 13*mm
    p.saveState()
    p.setFillColor(white)
    p.rect((width - ew)/2, height - top - eh , ew, eh, stroke=1, fill=1)
    p.setFillColor(black)
    p.setFont(font_bld, 20)
    p.drawCentredString(width/2, height - top - eh/2, cabecera['letra'])
    p.setFont(font_bld, 10)
    p.drawCentredString(width/2, height - top - eh + 7, 'COD.' + cabecera['codigo'])
    p.restoreState()


def post_encabezado(p, cabecera):
    top = margin + 60*mm
    ew = width - 2*margin
    eh = 8*mm
    th = 10

    p.saveState()
    p.rect((width - ew)/2, height - top - eh , ew, eh, stroke=1, fill=0)

    t = p.beginText(margin + 17*mm, height - top - 15)

    # Período desde
    t.setFont(font_bld, th)
    t.textOut(u'Período Facturado Desde: ')
    t.setFont(font_std, th)
    t.textOut(cabecera['desde'])

    # ... hasta
    t.setFont(font_bld, th)
    t.textOut(u'    Hasta: ')
    t.setFont(font_std, th)
    t.textOut(cabecera['hasta'])

    #
    t.setFont(font_bld, th)
    t.textOut(u'    Fecha Vencimiento Pago: ')
    t.setFont(font_std, th)
    t.textOut(cabecera['vencimiento'])

    p.drawText(t)

    p.restoreState()


def datos_cliente(p, cliente):
    top = margin + 68*mm
    ew = width - 2*margin
    eh = 25*mm
    th = 10

    p.saveState()
    p.rect((width - ew)/2, height - top - eh , ew, eh, stroke=1, fill=0)

    t = p.beginText(1.5*margin, height - top - 15)

    # Razón Social
    t.setFont(font_bld, th)
    t.textOut(u'Apellido y Nombre / Razón Social: ')
    t.setFont(font_std, th)
    t.textLine(cliente['nombre'])

    # Domicilio
    t.setFont(font_bld, th)
    t.textOut(u'Domicilio Comercial: ')
    t.setFont(font_std, th)
    t.textLine(cliente['direccion'])

    # CUIT
    t.setFont(font_bld, th)
    t.textOut(u'CUIT: ' if len(cliente['CUIT']) > 10 else u'DNI: ')
    t.setFont(font_std, th)
    t.textLine(cliente['CUIT'])

    # Condición frente al IVA
    t.setFont(font_bld, th)
    t.textOut(u'Condición frente al IVA: ')
    t.setFont(font_std, th)
    t.textLine(cliente['condicion_iva'])

    # Condición de venta
    t.setFont(font_bld, th)
    t.textOut(u'Condición de venta: ')
    t.setFont(font_std, th)
    t.textLine(cliente['condicion_venta'])

    p.drawText(t)

    p.restoreState()


def detalle_lineas(p, header, sizes, lineas):
    tw = width - 2*margin
    table = Table(header + lineas, colWidths=[size * tw for size in sizes])
    table.setStyle([
	    ('FONT', (0, 0), (-1, -1), font_std),
	    ('FONT', (0, 0), (-1, 0), font_bld),
        ('LEADING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, 0), 0.5, black),
        ('BACKGROUND', (0, 0), (-1, 0), Color(0.8,0.8,0.8)),
        ('ALIGN', (1, 0), (-1, -1), 'CENTRE'),
        ('ALIGN', (1, 1), (-3, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ])
    mw, mh = table.wrapOn(p, width, height)
    table.drawOn(p, margin, height - 99*mm - mh)

def imprimir_mensaje(p, responsable, cabecera):

    if cabecera['id_tipo_comprobante'] != ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA:
        return

    mensaje = mensajes['mensaje_legal_factura_electronica'].split('\n')

    top = 170*mm
    ew = (width - 2*margin) / 2
    eh = 72*mm 
    y_pos = height - top - eh - 2

    p.saveState()
    p.rect( margin, y_pos , ew, eh, stroke=1, fill=0)
    p.setFont(font_std, 12)

    for line, i in zip(mensaje, range(len(mensaje))):
        p.drawString(margin * 2, y_pos + eh - margin - i*15 - 5, line)

    p.restoreState()


def detalle_iva(p, detalle):
    table = Table(detalle, [5*cm, 3*cm])
    table.setStyle([
	    ('FONT', (0, 0), (-1, -1), font_bld),
        ('LEADING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ])
    table.wrapOn(p, width, height)
    table.drawOn(p, width - margin - 8*cm, 55*mm)


def pie_de_pagina(p, responsable, imprimir_leyenda_honorarios):
    mensaje = mensajes['mensaje_leyenda_honorarios'] if imprimir_leyenda_honorarios else u''
    top = 250*mm
    ew = width - 2*margin
    eh = 7*mm if mensaje else 0

    p.saveState()
    p.rect((width - ew)/2, height - top - eh - 3 , ew, eh, stroke=1, fill=0)
    p.setFont(font_std, 12)
    p.drawCentredString(width/2, height - top - eh/2 - 6, mensaje)
    p.restoreState()


def generar_factura(response, comp, leyenda):
    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle(obtener_filename(comp['responsable'], comp['cabecera']))

    for copia in ['Original', 'Duplicado', 'Triplicado']:

        p.setLineWidth(0.5)

        # Escribe encabezado
        encabezado(p, copia)

        zona_izquierda(p, comp['responsable'])

        zona_derecha(p, comp['cabecera'], comp['responsable'])

        zona_central(p, comp['cabecera'])

        post_encabezado(p, comp['cabecera'])

        datos_cliente(p, comp['cliente'])

        detalle_lineas(p, comp['headers'], comp['sizes'], comp['lineas'])

        imprimir_mensaje(p, comp['responsable'], comp['cabecera'])

        detalle_iva(p, comp['detalle'])

        pie_de_pagina(p, comp['responsable'], leyenda)

        # Escribe código de barras
        codigo_barra_i25(p, comp['cabecera'])

        # Escribe el CAE y la fecha
        cae_y_fecha(p, comp['cabecera'])

        # Close the PDF object cleanly, and we're done.
        p.showPage()

    p.save()
    return response


def obtener_codigo_barras(c):
    r = responsables[c.responsable.lower()]
    x = u'{0}{1:02d}{2:04d}{3}{4}'.format(
        r['CUIT'].replace('-', ''),
        c.codigo_afip,
        c.nro_terminal,
        c.cae,
        c.vencimiento_cae.strftime('%Y%m%d')
        )
    return int(x)


def format_gravado_linea(grav):
    return u'{0}%'.format(grav.porcentaje) if grav.porcentaje else grav.descripcion


def format_gravado_detalle(grav):
    return u'Importe Neto Gravado: $' if grav.porcentaje else u'Importe Excento: $'


def obtener_subtotal_comprobante(c):
    return u'{0:.2f}'.format(c.importe_gravado_afip)


def obtener_iva_comprobante(c, iva):
    return c.importe_alicuota_afip if c.gravado.porcentaje == iva else 0.0


def obtener_lineas_comprobante(c):
    styles = styles=getSampleStyleSheet()
    if c.sub_tipo.upper() == 'A':
        return [[Paragraph(l.concepto.replace(u'\r',u'').replace(u'\n',u'<br/>'), styles["Normal"]), u'{0:.2f}'.format(l.importe_neto), format_gravado_linea(c.gravado), u'{0:.2f}'.format(l.sub_total)] for l in c.lineas.all()]
    else:
        return [[Paragraph(l.concepto.replace(u'\r',u'').replace(u'\n',u'<br/>'), styles["Normal"]), u'{0:.2f}'.format(l.sub_total)] for l in c.lineas.all()]


def obtener_headers_lineas(c):
    if c.sub_tipo.upper() == 'A':
        return [[u'Producto / Servicio', u'Subtotal', u'Alícuota IVA', u'Subtotal c/IVA']]
    else:
        return [[u'Producto / Servicio', u'Subtotal']]


def obtener_headers_sizes(c):
    if c.sub_tipo.upper() == 'A':
        return [0.6, 0.14, 0.12, 0.14]
    else:
        return [0.86, 0.14]


def obtener_detalle_iva(c):
    ivas = [27, 21, 10.5, 5, 2.5, 0]
    if c.sub_tipo.upper() == 'A':
        result = [
            [format_gravado_detalle(c.gravado), obtener_subtotal_comprobante(c)],
            [u'', u'']
        ]

        result += [
            [u'IVA {0}%: $'.format(iva), u'{0:.2f}'.format(obtener_iva_comprobante(c, iva))]
            for iva in ivas
            ]
    else:
        result = [
            [u'Subtotal: $', u'{0:.2f}'.format(c.total_facturado)],
            [u'', u'']
        ]

        result += [[u'', u''] for _ in ivas]

    result += [
        [u'Importe Otros Tributos: $', u'0.00'],
        [u'Importe Total: $', u'{0:.2f}'.format(c.total_facturado)],
    ]
    return result

def format_tipo_comprobante(nombre):

    if len(nombre) <= max_char:
        return nombre
    
    result = ''
    amount_chars = 0
    
    for word in nombre.split(' '):
        amount_chars += len(word)
        if amount_chars > max_char:
            result += '\n'
            amount_chars = 0
        result += word + ' '
    
    return result

def obtener_comprobante(cae):
    c = Comprobante.objects.get(cae=cae)

    return {
        'cabecera': {
            'codigo': u'{0:02d}'.format(c.codigo_afip),
            'tipo': format_tipo_comprobante(c.tipo_comprobante.nombre),
            'id_tipo_comprobante': c.tipo_comprobante.id,
            'letra': c.sub_tipo,
            'punto_venta': c.nro_terminal,
            'numero': c.numero,
            'fecha': c.fecha_emision.strftime('%d/%m/%Y'),
            'desde': u'  /  /    ',
            'hasta': u'  /  /    ',
            'vencimiento': (c.fecha_vencimiento).strftime('%d/%m/%Y'),
            'CAE': c.cae,
            'CAE_vencimiento': c.vencimiento_cae.strftime('%d/%m/%Y'),
            'codigo_barras': obtener_codigo_barras(c),
        },
        'cliente': {
            'CUIT': c.nro_cuit,
            'nombre': c.nombre_cliente,
            'condicion_iva': c.condicion_fiscal,
            'condicion_venta': u'Otra',
            'direccion': c.domicilio_cliente,
        },
        'responsable': responsables[c.responsable.lower()],
        'headers': obtener_headers_lineas(c),
        'sizes': obtener_headers_sizes(c),
        'lineas': obtener_lineas_comprobante(c),
        'detalle': obtener_detalle_iva(c)
    }


def obtener_filename(responsable, encabezado):
    return u'{0}_{1}_{2:04d}_{3:08d}'.format(
        responsable['CUIT'],
        encabezado['codigo'],
        encabezado['punto_venta'],
        encabezado['numero'],
        )
