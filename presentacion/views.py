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
from comprobante.afip import Afip, AfipErrorRed, AfipErrorValidacion

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

    def perform_create(self, serializer):
        obra_social = ObraSocial.objects.get(pk=serializer.data['obra_social_id'])
        periodo = serializer.validated_data['periodo']
        fecha = serializer.validated_data['fecha']
        estado = serializer.validated_data['estado']
        estudios_data = serializer.data['estudios']
        comprobante_data = serializer.validated_data['comprobante']
        nro_comprobante = comprobante_data['numero']
        tipo_comprobante = TipoComprobante.objects.get(pk=comprobante_data['tipo_id'])
        sub_tipo = comprobante_data['sub_tipo']
        nro_terminal = comprobante_data['nro_terminal']
        responsable = comprobante_data['responsable']
        gravado = Gravado.objects.get(pk=comprobante_data['gravado_id'])
        presentacion = None

        assert responsable in ('Cedir', 'Brunetti')
        assert sub_tipo in ('A', 'B')
        assert not (obra_social.is_particular_or_especial())
        # REFACTOR: no se me ocurrio una mejor forma de hacer este chequeo
        # Si ya existe esta tupla de comprobante, queremos que falle ahora.
        try:
            Comprobante.objects.get(numero=nro_comprobante, responsable=responsable,
                tipo_comprobante=tipo_comprobante, sub_tipo=sub_tipo, nro_terminal=nro_terminal)
            assert False
        except :
            pass
        for estudio_data in estudios_data:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            assert(estudio.obra_social) == obra_social

        neto = sum([Decimal(e['importe_estudio']) for e in estudios_data])
        iva = neto * gravado.porcentaje
        total = neto + iva
        if estado == Presentacion.PENDIENTE:
            comprobante = Comprobante(
                nombre_cliente=obra_social.nombre,
                domicilio_cliente=obra_social.direccion,
                nro_cuit=obra_social.nro_cuit,
                condicion_fiscal=obra_social.condicion_fiscal,
                responsable=responsable,
                tipo_comprobante=tipo_comprobante,
                sub_tipo=sub_tipo,
                nro_terminal=nro_terminal,
                estado=Comprobante.NO_COBRADO,
                numero=nro_comprobante,
                total_facturado=total,
                fecha_emision=date.today(),
                gravado=gravado,
            )
            linea = LineaDeComprobante(
                comprobante=comprobante,
                concepto='FACTURACION CORRESPONDIENTE A ' + periodo,
                importe_neto=neto,
                iva=iva,
                sub_total=total
            )
            try:
                Afip().emitir_comprobante(comprobante, [linea])
            except AfipErrorRed as e:
                content = {'data': {}, 'message': 'No se pudo realizar la conexion con Afip, intente mas tarde.\nError: ' + str(e)}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except AfipErrorValidacion as e:
                content = {'data': {}, 'message': 'Afip rechazo el comprobante.\nError: ' + str(e)}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            presentacion = Presentacion(
                obra_social=obra_social,
                comprobante=comprobante,
                fecha=fecha,
                estado=Presentacion.PENDIENTE,
                periodo=periodo,
                iva=iva,
                total=neto,
                total_facturado=total
            )
            comprobante.save()
            linea.save()
        elif Presentacion.ABIERTO:
            presentacion = Presentacion(
                obra_social=obra_social,
                comprobante=None,
                fecha=fecha,
                estado=Presentacion.ABIERTO,
                periodo=periodo,
                iva=iva,
                total=neto,
                total_facturado=total
            )

        for estudio_data in estudios_data:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            estudio.nro_de_orden = estudio_data['nro_de_orden']
            estudio.importe_estudio = estudio_data['importe_estudio']
            estudio.pension = estudio_data['pension']
            estudio.diferencia_paciente = estudio_data['diferencia_paciente']
            estudio.arancel_anestesia = estudio_data['arancel_anestesia']
            estudio.save()
        presentacion.save()

    # def perform_update(self, serializer):
    #     pass


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