# -*- coding: utf-8
from comprobante.models import Comprobante
from datetime import date


def obtener_comprobantes_ventas(responsable, anio, mes):
    anio = int(anio)
    mes = int(mes)
    is_december = not mes % 12  # True if mes is december, False otherwise
    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio + int(is_december), 1 + mes % 12, 1)
    return Comprobante.objects\
        .filter(responsable__iexact=responsable, fecha_emision__gte=primer_dia, fecha_emision__lt=ultimo_dia)\
        .exclude(tipo_comprobante=2)\
        .order_by('nro_terminal', 'fecha_emision', 'numero')


def obtener_archivo_ventas(comprobantes):
    return [obtener_linea_ventas(c) for c in comprobantes], [obtener_lineas_alicuota(c) for c in comprobantes]


def obtener_lineas_alicuota(c):
    return u'{1:03}{0.nro_terminal:05}{0.numero:020}{3:015}{2:04}{4:015}'.format(c, c.codigo_afip, c.codigo_alicuota_afip, int(100 * c.importe_gravado_afip), int(100 * c.importe_alicuota_afip))


def obtener_linea_ventas(c):
    return u'{0.fecha_emision:%Y%m%d}{1:03}{0.nro_terminal:05}{0.numero:020}{0.numero:020}{2:02}{3}{0.nombre_cliente:<30.30}{4:015}{5:015}{5:015}{6:015}{5:015}{5:015}{5:015}{5:015}PES00010000001{7}{5:015}{8:%Y%m%d}'.format(c, c.codigo_afip, c.tipo_id_afip, c.nro_id_afip.zfill(20), int(100 * c.total_facturado), 0, int(100 * c.importe_excento_afip), c.codigo_operacion_afip, c.fecha_vencimiento)
