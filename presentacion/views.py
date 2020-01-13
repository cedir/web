import simplejson
from datetime import date
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from common.drf.views import StandardResultsSetPagination

from presentacion.models import Presentacion
from presentacion.serializers import PresentacionSerializer, PresentacionRetrieveSerializer, PresentacionCreateUpdateSerializer, PresentacionCreateUpdateSerializer
from presentacion.obra_social_custom_code.osde_presentacion_digital import \
    OsdeRowEstudio, OsdeRowMedicacion, OsdeRowPension, OsdeRowMaterialEspecifico
from presentacion.obra_social_custom_code.amr_presentacion_digital import AmrRowEstudio
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer
from obra_social.models import ObraSocial
from comprobante.models import Comprobante, LineaDeComprobante, Gravado, TipoComprobante
from comprobante.afip import AfipErrorRed, AfipErrorValidacion, AfipError

class PresentacionViewSet(viewsets.ModelViewSet):
    queryset = Presentacion.objects.all().order_by('-fecha')
    serializer_class = PresentacionSerializer
    filter_fields = ('obra_social',)
    pagination_class = StandardResultsSetPagination
    page_size = 50

    serializers = {
        'retrieve': PresentacionRetrieveSerializer,
        'create': PresentacionCreateUpdateSerializer,
        'update': PresentacionCreateUpdateSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)

    def create(self, request, *args, **kwargs):
        try:
            return super(PresentacionViewSet, self).create(request, *args, **kwargs)
        except AfipErrorRed as e:
            content = u'No se pudo realizar la conexion con Afip, intente mas tarde.\nError: ' + unicode(e)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AfipErrorValidacion as e:
            content = u'Afip rechazo el comprobante. \nError: ' + unicode(e)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AfipError as e:
            content = u'Error no especificado de Afip. \nError: ' + unicode(e)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @detail_route(methods=['get'])
    def get_detalle_osde(self, request, pk=None):

        presentacion = Presentacion.objects.get(pk=pk)

        csv_string = ''
        estudios = presentacion.estudios.all()

        try:
            for estudio in estudios:
                csv_string = '{}\n{}'.format(csv_string, OsdeRowEstudio(estudio).get_row_osde())

                if estudio.get_total_medicacion():
                    csv_string = '{}\n{}'.format(csv_string, OsdeRowMedicacion(estudio).get_row_osde())
                if estudio.pension:
                    csv_string = '{}\n{}'.format(csv_string, OsdeRowPension(estudio).get_row_osde())
                for material_esp in estudio.estudioXmedicamento.filter(medicamento__tipo=u'Mat Esp'):
                    csv_string = '{}\n{}'.format(csv_string, OsdeRowMaterialEspecifico(estudio, material_esp).get_row_osde())

            response = HttpResponse(csv_string, content_type='text/plain')
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')

        return response

    @detail_route(methods=['get'])
    def get_detalle_amr(self, request, pk=None):
        presentacion = Presentacion.objects.get(pk=pk)
        csv_string = ''
        estudios = presentacion.estudios.all().order_by('fecha', 'id')
        try:
            comprobante = presentacion.comprobante

            for estudio in estudios:
                csv_string = '{}\n{}'.format(csv_string, AmrRowEstudio(estudio, comprobante).get_row())

            response = HttpResponse(csv_string, content_type='text/plain')
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
        return response

    @detail_route(methods=['get'])
    def estudios(self, request, pk=None):
        presentacion = Presentacion.objects.get(pk=pk)
        estudios = presentacion.estudios.all().order_by('fecha', 'id')
        try:
            response = JsonResponse(EstudioDePresetancionRetrieveSerializer(estudios, many=True).data, safe=False)
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
        return response

    # @detail_route(methods=['patch'])
    # def cerrar(self, request, pk=None):
    #     # Parametros: importes que cambian, importe final.
    #     # Validar que esta ABIERTA.
    #     # Pasar a PENDIENTE. Generar comprobante.
    #     presentacion = Presentacion.objects.get(pk=pk)
    #     try:
    #         response = HttpResponse(simplejson.dumps({'error': "Not Implemented"}), status=500, content_type='application/json')
    #     except Exception as ex:
    #         response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
    #     return response

    # @detail_route(methods=['patch'])
    # def abrir(self, request, pk=None):
    #     # Validar que esta PENDIENTE
    #     # Pasar a ABIERTA.
    #     # Anular comprobante y generar una nota?
    #     presentacion = Presentacion.objects.get(pk=pk)
    #     try:
    #         response = HttpResponse(simplejson.dumps({'error': "Not Implemented"}), status=500, content_type='application/json')
    #     except Exception as ex:
    #         response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
    #     return response

    # @detail_route(methods=['patch'])
    # def cobrar(self, request, pk=None):
    #     # Verificar que esta PENDIENTE
    #     # Pasar a COBRADA
    #     # Setear valores cobrados de estudios
    #     # Generar un PagoPresentacion
    #     presentacion = Presentacion.objects.get(pk=pk)
    #     try:
    #         response = HttpResponse(simplejson.dumps({'error': "Not Implemented"}), status=500, content_type='application/json')
    #     except Exception as ex:
    #         response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
    #     return response