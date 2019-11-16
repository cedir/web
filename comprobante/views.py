# -*- coding: utf-8
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from decimal import Decimal

import zipfile
import StringIO

from imprimir import generar_factura, obtener_comprobante, obtener_filename
from informe_ventas import obtener_comprobantes_ventas, obtener_archivo_ventas

from comprobante.serializers import ComprobanteListadoSerializer, ComprobanteSerializer, ComprobanteSmallSerializer
from comprobante.models import Comprobante
from comprobante.calculador_informe import calculador_informe_factory
from comprobante.comprobante_asociado import crear_comprobante_asociado, TipoComprobanteAsociadoNoValidoException
from comprobante.afip import AfipErrorRed, AfipErrorValidacion

from common.drf.views import StandardResultsSetPagination

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

class InformeMensualView(generics.ListAPIView):
    serializer_class = ComprobanteListadoSerializer

    def list(self, request):
        comprobantes = Comprobante.objects.exclude(estado=Comprobante.ANULADO)
        queryset = comprobantes.filter(fecha_emision__month=request.query_params["mes"],
                                       fecha_emision__year=request.query_params["anio"])
        data = [ComprobanteListadoSerializer(q, context={'calculador': calculador_informe_factory(q)}).data
                for q in queryset]
        return Response(data)

class ComprobanteViewSet(viewsets.ModelViewSet):
    queryset = Comprobante.objects.all()
    serializer_class = ComprobanteSerializer
    page_size = 50
    pagination_class = StandardResultsSetPagination

    @list_route(methods=['POST'])
    def crear_comprobante_asociado(self, request, pk=None):
        id_comprobante_asociado = int(request.POST['id-comprobante-asociado'])
        importe = Decimal(request.POST['importe'])
        id_tipo_nuevo_comprobante = int(request.POST['id-tipo'])

        try:
            comp = crear_comprobante_asociado(id_comprobante_asociado, importe, id_tipo_nuevo_comprobante)
            content = {'data': ComprobanteSmallSerializer(comp).data , 'message': 'Comprobante creado correctamente'}
            return Response(content, status=status.HTTP_201_CREATED)
        except Comprobante.DoesNotExist:
            content = {'data': {}, 'message': 'El comprobante seleccionado no existe en la base de datos.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except TipoComprobanteAsociadoNoValidoException:
            content =  {'data': {}, 'message': 'No se puede crear un comprobante asociado con el tipo seleccionado.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except AfipErrorRed as e:
            content = {'data': {}, 'message': 'No se pudo realizar la conexion con Afip, intente mas tarde.\nError: ' + str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AfipErrorValidacion:
            content = {'data': {}, 'message': 'Afip rechazo el comprobante.\nError: ' + str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
