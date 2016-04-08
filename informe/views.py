# -*- coding: utf-8
from django.http import HttpResponse
from comprobante.models import Comprobante
from datetime import date


def obtener_comprobantes(responsable, anio, mes):
    anio = int(anio)
    mes = int(mes)
    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio, 1 + mes % 12, 1)
    return Comprobante.objects\
        .filter(responsable__iexact=responsable, fechaemision__gte=primer_dia, fechaemision__lt=ultimo_dia)\
        .exclude(idtipocomprobante=2)\
        .order_by('nroterminal', 'fechaemision', 'nrocomprobante')


def obtener_archivo_ventas(comprobantes):
    return [ obtener_linea_ventas(c) for c in comprobantes]


def obtener_linea_ventas(c):
    return u'{0.fechaemision:%Y%m%d}{1:03}{0.nroterminal:05}{0.nrocomprobante:020}{0.nrocomprobante:020}{2:02}{3}{0.nombrecliente:<30.30}{4:015}{5:015}{5:015}{6:015}{5:015}{5:015}{5:015}{5:015}PES00010000001{7}{5:015}{8:%Y%m%d}\r\n'.format(c, c.codigo_afip, c.tipo_id_afip, c.nro_id_afip.zfill(20), c.importe_afip, 0, c.importe_excento_afip, c.codigo_operacion_afip, c.fecha_vencimiento)


# Create your views here.
def ventas(request, responsable, anio, mes):
    # Adquiere datos
    comprobantes = obtener_comprobantes(responsable, anio, mes)

    # Genera el archivo
    content = obtener_archivo_ventas(comprobantes)

    # Devuelve la respuesta
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = u'attachment; filename="VENTAS.txt"'

    return response
