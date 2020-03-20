import simplejson
from datetime import date
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from common.drf.views import StandardResultsSetPagination

from presentacion.models import Presentacion
from presentacion.serializers import PresentacionSerializer, PresentacionRetrieveSerializer, PresentacionCreateSerializer, PresentacionUpdateSerializer
from presentacion.obra_social_custom_code.osde_presentacion_digital import \
    OsdeRowEstudio, OsdeRowMedicacion, OsdeRowPension, OsdeRowMaterialEspecifico
from presentacion.obra_social_custom_code.amr_presentacion_digital import AmrRowEstudio
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer
from obra_social.models import ObraSocial
from comprobante.models import Comprobante, LineaDeComprobante, Gravado, TipoComprobante, \
    ID_TIPO_COMPROBANTE_LIQUIDACION
from comprobante.afip import Afip, AfipErrorRed, AfipErrorValidacion, AfipError
from comprobante.serializers import comprobante_cerrar_presentacion_serializer_factory

class PresentacionViewSet(viewsets.ModelViewSet):
    queryset = Presentacion.objects.all().order_by('-fecha')
    serializer_class = PresentacionSerializer
    filter_fields = ('obra_social',)
    pagination_class = StandardResultsSetPagination
    page_size = 50

    serializers = {
        'retrieve': PresentacionRetrieveSerializer,
        'create': PresentacionCreateSerializer,
        'update': PresentacionUpdateSerializer,
        'partial_update': PresentacionUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)

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

    @detail_route(methods=['patch'])
    def cerrar(self, request, pk=None):
        # Validar que esta ABIERTO.
        # Pasar a PENDIENTE.
        # Generar comprobante.

        # Pasar cosas de Comprobante a un serializer?
        try:
            presentacion = Presentacion.objects.get(pk=pk)
            if presentacion.estado != Presentacion.ABIERTO:
                raise ValidationError("La presentacion debe estar en estado ABIERTO")
            obra_social = presentacion.obra_social
            comprobante_data = request.data
            comprobante_data["neto"] = sum([Decimal(e.importe_estudio) for e in presentacion.estudios.all()])
            comprobante_data["nombre_cliente"] = obra_social.nombre
            comprobante_data["domicilio_cliente"] = obra_social.direccion
            comprobante_data["nro_cuit"] = obra_social.nro_cuit
            comprobante_data["condicion_fiscal"] = obra_social.condicion_fiscal
            comprobante_serializer = comprobante_cerrar_presentacion_serializer_factory(data=comprobante_data)
            comprobante_serializer.is_valid(raise_exception=True)
            comprobante = comprobante_serializer.save()
            linea = comprobante.lineas.first()
            presentacion.estado = Presentacion.PENDIENTE
            presentacion.total = linea.importe_neto
            presentacion.iva = linea.iva
            presentacion.total_facturado = linea.sub_total
            presentacion.save()
            response = JsonResponse(PresentacionSerializer(presentacion).data, safe=False)

        except ValidationError as ex:
            response = Response(ex.message, status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
        return response

    @detail_route(methods=['patch'])
    def abrir(self, request, pk=None):
        # Validar que esta PENDIENTE
        # Pasar a ABIERTA.
        # Anular comprobante y generar una nota?
        try:
            presentacion = Presentacion.objects.get(pk=pk)
            if presentacion.estado != Presentacion.PENDIENTE:
                return HttpResponse(simplejson.dumps({'error': "La presentacion debe estar en estado PENDIENTE"}), status=400, content_type='application/json')
            presentacion.comprobante.anular()
            presentacion.comprobante = None
            presentacion.estado = Presentacion.ABIERTO
            presentacion.save()
            return JsonResponse(PresentacionSerializer(presentacion).data, safe=False)
        except Exception as ex:
            return HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')

    @detail_route(methods=['patch'])
    def cobrar(self, request, pk=None):
        # Verificar que esta PENDIENTE
        # Pasar a COBRADA
        # Setear valores cobrados de estudios
        # Generar un PagoPresentacion
        try:
            response = HttpResponse(simplejson.dumps({'error': "Not Implemented"}), status=500, content_type='application/json')
            presentacion = Presentacion.objects.get(pk=pk)
            if presentacion.estado != Presentacion.PENDIENTE:
                return HttpResponse(simplejson.dumps({'error': "La presentacion debe estar en estado PENDIENTE"}), status=400, content_type='application/json')
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
        return response