# -*- coding: utf-8
from django.http import HttpResponse

from imprimir import generar_factura, obtener_comprobante, obtener_filename

def imprimir(request, cae):
    # Adquiere datos
    comp = obtener_comprobante(cae)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="{0}.pdf"'.format(obtener_filename(comp['responsable'], comp['cabecera']))

    return generar_factura(response, comp)
