# -*- coding: utf-8
from django.http import HttpResponse
from comprobante.models import Comprobante
from datetime import date

import zipfile
import StringIO


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
    return [obtener_linea_ventas(c) for c in comprobantes], [obtener_lineas_alicuota(c) for c in comprobantes]


def obtener_lineas_alicuota(c):
    return u'{1:03}{0.nroterminal:05}{0.nrocomprobante:020}{3:015}{2:04}{4:015}'.format(c, c.codigo_afip, c.codigo_alicuota_afip, c.importe_gravado_afip, c.importe_alicuota_afip)


def obtener_linea_ventas(c):
    return u'{0.fechaemision:%Y%m%d}{1:03}{0.nroterminal:05}{0.nrocomprobante:020}{0.nrocomprobante:020}{2:02}{3}{0.nombrecliente:<30.30}{4:015}{5:015}{5:015}{6:015}{5:015}{5:015}{5:015}{5:015}PES00010000001{7}{5:015}{8:%Y%m%d}'.format(c, c.codigo_afip, c.tipo_id_afip, c.nro_id_afip.zfill(20), c.importe_afip, 0, c.importe_excento_afip, c.codigo_operacion_afip, c.fecha_vencimiento)


# Create your views here.
def ventas(request, responsable, anio, mes):
    # Adquiere datos
    comprobantes = obtener_comprobantes(responsable, anio, mes)

    # Genera el archivo
    (ventas, alicuotas) = obtener_archivo_ventas(comprobantes)

    # Abre un StringIO para guardar el contenido del archivo
    stream = StringIO.StringIO()

    # Compresor zip
    zipcomp = zipfile.ZipFile(stream, 'w')

    # Agrega los archivos
    zipcomp.writestr(u'VENTAS.txt', u'\r\n'.join(ventas).encode('ascii', 'replace'))
    zipcomp.writestr(u'ALICUOTAS.txt', u'\r\n'.join(alicuotas).encode('ascii', 'replace'))

    # Cierra el archivo y escribe el contenido
    zipcomp.close()

    # Genera el response adecuado
    resp = HttpResponse(stream.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename={0}_{1}_{2}.zip'.format(responsable, anio, mes)

    return resp
