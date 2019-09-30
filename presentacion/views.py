import simplejson
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from common.drf.views import StandardResultsSetPagination
from estudio.models import Estudio
from presentacion.models import Presentacion
from presentacion.serializers import PresentacionSerializer, PresentacionRetrieveSerializer, PresentacionCreateUpdateSerializer
from presentacion.obra_social_custom_code.osde_presentacion_digital import \
    OsdeRowEstudio, OsdeRowMedicacion, OsdeRowPension, OsdeRowMaterialEspecifico
from presentacion.obra_social_custom_code.amr_presentacion_digital import AmrRowEstudio


class PresentacionViewSet(viewsets.ModelViewSet):
    queryset = Presentacion.objects.all().order_by('-fecha')
    serializer_class = PresentacionSerializer
    filter_fields = ('obra_social',)
    pagination_class = StandardResultsSetPagination
    page_size = 50

    """
    POST presentection/  --> crea presentacion
    PATCH presentacion/123   -> finalizar  (validar que esta en estado abierta, sino no se puede modificar)
    PATCH presentacion/123/cobrar  -->validar que esta en estado pendiente
    PATCH presentacion/123/abrir  -->validar que esta en estado pendiente (anula comprobante y cambia estado, etc)
    GET presentacion/20  --> este se puede usar para cargar cualqueir pantalla (cobro, ver detalle, actulizar presentacion abierta)
    GET presenctacion/get_estudios_sin_presentar
    LIST presentacion
    """

    serializers = {
        'retrieve': PresentacionRetrieveSerializer,
        'create': PresentacionCreateUpdateSerializer,
        'update': PresentacionCreateUpdateSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)

    def perform_create(self, serializer):
        pass

    def perform_update(self, serializer):
        pass

    @list_route(methods=['get'])
    def get_estudios_sin_presentar(self, request):
        #presentacion = Presentacion(obra_social_id=2)
        #presentacion.estudios = Estudio.objects.filter()[:10]

        # TODO: ver como hacer para usar el mismo serializar tanto para GET como para este metodo donde no hay una instancia
        presentacion = Presentacion.objects.filter(estado=2).last()
        serializer = PresentacionRetrieveSerializer(presentacion)

        return Response(serializer.data)

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
