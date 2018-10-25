# -*- coding: utf-8
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect

import zipfile
import StringIO

from imprimir import generar_factura, obtener_comprobante, obtener_filename
from informe_ventas import obtener_comprobantes_ventas, obtener_archivo_ventas
from comprobante.serializers import ComprobanteListadoSerializer


def imprimir(request, cae):
    # Imprime leyenda?
    leyenda = request.method == 'GET' and 'leyenda' in request.GET

    # Adquiere datos
    comp = obtener_comprobante(cae)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="{0}.pdf"'.format(obtener_filename(comp['responsable'], comp['cabecera']))

    return generar_factura(response, comp, leyenda)


def ventas(request, responsable, anio, mes):
    if not request.user.is_authenticated() or not request.user.has_perm('comprobante.informe_ventas'):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    # Adquiere datos
    comprobantes = obtener_comprobantes_ventas(responsable, anio, mes)

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


from rest_framework import generics
from comprobante.models import Comprobante
from rest_framework.response import Response
class InformeMensualView(generics.ListAPIView):
    serializer_class = ComprobanteListadoSerializer

    def list(self, request):
        #import pdb; pdb.set_trace()
        queryset = Comprobante.objects.filter(fecha_emision__month=request.query_params["mes"],
                                              fecha_emision__year=request.query_params["anio"])
        data = [ComprobanteListadoSerializer(q, context={'calculador': 1}).data
                for q in queryset]
        return Response(data)

"""
- traer comprobantes filtrando por fecha desde - fecha hasta
- para cada comprobante hay que calcular los honorarios
- el "calcular honorarios" devuelve 3 importes nuevos: honorario, anestesia y total medicacion
- Con el comprobante se trae la presentacion asociada
- Con la presentacion se cargan las lineasDePresentacion
- Para cada linea, se obtiene el estudio
- Con el estudio se calculan el honorario del medico (esta logica se comparte con Pago a Medico), el total medicacion y anestesia.
  (https://github.com/cedir/intranet/blob/81f708d089f02efd8d98c886782572428752913f/CedirNegocios/Interfaces/CalculadorHonorariosComprobantes.vb#L79)
- Finalmente se muestran los datos de comprobante (*) mas honorario, anestesia y total medicacion

NOTA: el calculo de honorario medico se aplican las mismas reglas que pago a medico. Si el estudio esta pagado al medico, no importa, volver a aplicar las reglas porque hay qye mostrar lo que se deberia pagar, y no lo que se pago.
      calculo de honorario anestesia sale del campo "anestesia" del estudio. Sino esta cargado se muestra 0 (cero)

NOTA 2: del calculo de pago a medico, se desprenden otros valores como "Retencion Impositiva" y "Gastos Administriativos".
        Estos valores deben ser sumados por separado y mostrado en diferentes columnas.





"""
