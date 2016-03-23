# -*- coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse

from comprobante.models import *

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import black,white, Color
from reportlab.graphics.barcode.common import I2of5
from reportlab.platypus import Table

from textwrap import wrap

width, height = A4
margin = 6*mm
font_std = 'Helvetica'
font_bld = 'Helvetica-Bold'

def digito_verificador_modulo10(numero):
    "Rutina para el cálculo del dígito verificador 'módulo 10'"
    codigo = str(numero)
    # Ver RG 1702 AFIP
    # Etapa 1: comenzar desde la izquierda, sumar todos los caracteres ubicados en las posiciones impares.
    etapa1 = sum([int(c) for i,c in enumerate(codigo) if not i%2])
    # Etapa 2: multiplicar la suma obtenida en la etapa 1 por el número 3
    etapa2 = etapa1 * 3
    # Etapa 3: comenzar desde la izquierda, sumar todos los caracteres que están ubicados en las posiciones pares.
    etapa3 = sum([int(c) for i,c in enumerate(codigo) if i%2])
    # Etapa 4: sumar los resultados obtenidos en las etapas 2 y 3.
    etapa4 = etapa2 + etapa3
    # Etapa 5: buscar el menor número que sumado al resultado obtenido en la etapa 4 dé un número múltiplo de 10.
    # Este será el valor del dígito verificador del módulo 10.
    digito = 10 - (etapa4 % 10)
    if digito == 10:
        digito = 0
    return numero*10 + digito

def codigo_barra_I25(canvas, cabecera):
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
        canvas.drawCentredString(x + (bc.width)/2, y - 3*mm, str(num))
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
    eh = 45*mm
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
    t.textLine(responsable['nombre'])

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
    eh = 45*mm
    th = 9
    ld = 28
    fc = 0.45

    p.saveState()
    p.rect(width - ew - margin, height - top - eh , ew, eh, stroke=1, fill=0)

    t = p.beginText(width - ew - margin + 17*mm, height - top - 30)

    # Descripción factura
    t.setFont(font_bld, 16)
    t.textLine(cabecera['tipo'])

    # Punto y Numero
    t.setFont(font_bld, th)
    t.setLeading(fc*ld)
    t.textLine(u'Punto de Venta: {punto_venta:04d}    Comp.Nro: {numero:08d}'.format(**cabecera) )

    # Fecha de emisión
    t.textOut(u'Fecha de Emisión: ')
    t.setFont(font_std, th)
    t.setLeading(ld)
    t.textLine(cabecera['fecha'])

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
    top = margin +55*mm
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
    top = margin + 63*mm
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
    t.textOut(u'CUIT: ')
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

def detalle_lineas(p, lineas):
    tw = width - 2*margin
    encabezado = [[u'Producto / Servicio', u'Subtotal', u'Alícuota IVA', u'Subtotal c/IVA']]
    table = Table(encabezado + lineas, [0.6*tw, 0.14*tw, 0.12*tw, 0.14*tw])
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
    table.wrapOn(p, width, height)
    table.drawOn(p, margin, height - 121*mm)

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

def pie_de_pagina(p, responsable):
    top = 250*mm
    ew = width - 2*margin
    eh = 7*mm
    p.saveState()
    p.rect((width - ew)/2, height - top - eh - 3 , ew, eh, stroke=1, fill=0)
    p.setFont(font_std, 12)
    p.drawCentredString(width/2, height - top - eh/2 - 6, responsable['mensaje'])
    p.restoreState()

def generar_factura(response, comp):
    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle(obtener_filename(comp['responsable'], comp['cabecera']))
    p.setLineWidth(0.5)

    for copia in ['Original', 'Duplicado', 'Triplicado']:
        #Escribe encabezado
        encabezado(p, copia)

        zona_izquierda(p, comp['responsable'])

        zona_derecha(p, comp['cabecera'], comp['responsable'])

        zona_central(p, comp['cabecera'])

        post_encabezado(p, comp['cabecera'])

        datos_cliente(p, comp['cliente'])

        detalle_lineas(p, comp['lineas'])

        detalle_iva(p, comp['detalle'])

        pie_de_pagina(p, comp['responsable'])

        #Escribe código de barras
        codigo_barra_I25(p, comp['cabecera'])

        #Escribe el CAE y la fecha
        cae_y_fecha(p, comp['cabecera'])

        # Close the PDF object cleanly, and we're done.
        p.showPage()

    p.save()
    return response

def obtener_comprobante(id):
    c = Comprobante.objects.get(id=id)

    return {
        'cabecera': {
            'codigo': '01',
            'tipo': c.idtipocomprobante.tipocomprobante,
            'letra': c.subtipo,
            'punto_venta': c.nroterminal,
            'numero': c.nrocomprobante,
            'fecha': c.fechaemision.strftime('%d/%m/%Y'),
            'desde': '12/02/2016',
            'hasta': '12/02/2016',
            'vencimiento': '14/03/2016',
            'CAE': c.cae,
            'CAE_vencimiento' : '24/03/2016',
            'codigo_barras': 201180706590100026611900662433120160324,
        },
        'cliente' : {
            'CUIT': c.nrocuit,
            'nombre': c.nombrecliente,
            'condicion_iva': c.condicionfiscal,
            'condicion_venta': 'Otra',
            'direccion': c.domiciliocliente,
        },
        'responsable' : {
            'CUIT': '20118070659',
            'nombre': u'Brunetti Jose Edgar Alberto',
            'direccion': u'Bv. Oroño 1564. - Rosario Sud, Santa Fe.',
            'condicion_iva': u'IVA Responsable Inscripto',
            'condicion_ib': 'Excento',
            'inicio_actividades': '02/01/1992',
            'mensaje': u'"MÉDICO GASTROENTERÓLOGO Mat. Nro. 9314"',
        },
        'lineas': [[l.concepto, l.importeneto, '', l.subtotal] for l in c.lineas.all()],
        'detalle': [
            ['Importe Excento: $', ' 1665.02'],
            ['',''],
            ['IVA 27%: $', '0.00'],
            ['IVA 21%: $', '0.00'],
            ['IVA 10.5%: $', '0.00'],
            ['IVA 5%: $', '0.00'],
            ['IVA 2.5%: $', '0.00'],
            ['IVA 0%: $', '0.00'],
            ['Importe Otros Tributos: $', '0.00'],
            ['Importe Total: $', '1665.02'],
        ]
    }

def obtener_filename(responsable, encabezado):
    return u'{0}_{1}_{2:04d}_{3:08d}.pdf'.format(
        responsable['CUIT'],
        encabezado['codigo'],
        encabezado['punto_venta'],
        encabezado['numero'],
        )

def obtener_response(responsable, encabezado):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'attachment; filename="{0}.pdf"'.format(
        obtener_filename(responsable, encabezado)
        )
    return response

def imprimir(request, id_comprobante):
    #adquiere datos
    comp = obtener_comprobante(id_comprobante)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = obtener_response(comp['responsable'], comp['cabecera'])

    return generar_factura(response, comp)
