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
from presentacion.serializers import PagoPresentacionSerializer, PresentacionCreateSerializer, PresentacionRetrieveSerializer, PresentacionSerializer, PresentacionUpdateSerializer
from presentacion.obra_social_custom_code.osde_presentacion_digital import \
    OsdeRowEstudio, OsdeRowMedicacion, OsdeRowPension, OsdeRowMaterialEspecifico
from presentacion.obra_social_custom_code.amr_presentacion_digital import AmrRowEstudio
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer
from obra_social.models import ObraSocial
from comprobante.models import Comprobante, LineaDeComprobante, Gravado, TipoComprobante, \
    ID_TIPO_COMPROBANTE_LIQUIDACION
from comprobante.afip import Afip, AfipErrorRed, AfipErrorValidacion, AfipError
from comprobante.serializers import crear_comprobante_serializer_factory

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
                csv_string = '{}{}\n'.format(csv_string, AmrRowEstudio(estudio, comprobante).get_row())

            response = HttpResponse(csv_string[:-1], content_type='text/plain')
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
        return response

    @detail_route(methods=['get'])
    def estudios(self, request, pk=None):
        presentacion = Presentacion.objects.get(pk=pk)
        sucursal = request
        estudios = presentacion.estudios.all().order_by('fecha', 'id')
        try:
            response = JsonResponse(EstudioDePresetancionRetrieveSerializer(estudios, many=True).data, safe=False)
        except Exception as ex:
            response = JsonResponse({'error': ex.message}, status=500)
        return response

    @detail_route(methods=['patch'])
    def cerrar(self, request, pk=None):
        # Validar que esta ABIERTO.
        # Pasar a PENDIENTE.
        # Generar comprobante.
        try:
            presentacion = Presentacion.objects.get(pk=pk)
            if presentacion.estado != Presentacion.ABIERTO:
                raise ValidationError("La presentacion debe estar en estado ABIERTO")
            obra_social = presentacion.obra_social
            comprobante_data = request.data
            comprobante_data["neto"] = presentacion.total
            comprobante_data["nombre_cliente"] = obra_social.nombre
            comprobante_data["domicilio_cliente"] = obra_social.direccion
            comprobante_data["nro_cuit"] = obra_social.nro_cuit
            comprobante_data["condicion_fiscal"] = obra_social.condicion_fiscal
            comprobante_data["concepto"] = "FACTURACION CORRESPONDIENTE A " + presentacion.periodo
            comprobante_data["fecha_emision"] = presentacion.fecha
            comprobante_serializer = crear_comprobante_serializer_factory(data=comprobante_data)
            comprobante_serializer.is_valid(raise_exception=True)
            comprobante = comprobante_serializer.save()
            linea = comprobante.lineas.first()
            presentacion.estado = Presentacion.PENDIENTE
            presentacion.comprobante = comprobante
            presentacion.total = linea.importe_neto
            presentacion.iva = linea.iva
            presentacion.total_facturado = linea.sub_total
            presentacion.save()
            response = JsonResponse(PresentacionSerializer(presentacion).data, safe=False)

        except ValidationError as ex:
            response = JsonResponse({'error': ex.message}, status=400)
        except Exception as ex:
            response = JsonResponse({'error': ex.message}, status=500)
        return response

    @detail_route(methods=['patch'])
    def abrir(self, request, pk=None):
        # Validar que esta PENDIENTE
        # Pasar a ABIERTA.
        # Anular comprobante y generar una nota
        try:
            presentacion = Presentacion.objects.get(pk=pk)
            if presentacion.estado != Presentacion.PENDIENTE:
                return JsonResponse({'error': "La presentacion debe estar en estado PENDIENTE"}, status=400)
            presentacion.comprobante.anular()
            presentacion.comprobante = None
            presentacion.estado = Presentacion.ABIERTO
            presentacion.save()
            return JsonResponse(PresentacionSerializer(presentacion).data, safe=False)
        except Exception as ex:
            return JsonResponse({'error': ex.message}, status=500)

    @detail_route(methods=['patch'])
    def cobrar(self, request, pk=None):
        # Verificar que esta PENDIENTE
        # Pasar a COBRADA
        # Setear valores cobrados de estudios, total de presentacion
        # Armar un PagoPresentacion
        try:
            presentacion = Presentacion.objects.get(pk=pk)
            if presentacion.estado != Presentacion.PENDIENTE:
                raise ValidationError("La presentacion debe estar en estado PENDIENTE")
            if 'estudios' not in request.data:
                raise ValidationError("El campo 'estudios' es necesario")
            if 'nro_recibo' not in request.data:
                raise ValidationError("El campo 'nro_recibo' es necesario")
            if 'retencion_impositiva' not in request.data:
                raise ValidationError("El campo 'retencion_impositiva' es necesario")
            estudios_data = request.data.get('estudios')
            if len(estudios_data) < presentacion.estudios.count():
                raise ValidationError("Faltan datos de estudios")
            for e in estudios_data:
                estudio = Estudio.objects.get(pk=e['id'])
                if estudio.presentacion != presentacion:
                    raise ValidationError("El estudio {0} no corresponde a esta presentacion".format(e['id']))
                estudio.importe_cobrado_pension = e['importe_cobrado_pension']
                estudio.importe_cobrado_arancel_anestesia = e['importe_cobrado_arancel_anestesia']
                estudio.importe_estudio_cobrado = e['importe_estudio_cobrado']
                estudio.importe_medicacion_cobrado = e['importe_medicacion_cobrado']
                estudio.save()
            presentacion.total = sum([
                e.importe_cobrado_pension
                + e.importe_cobrado_arancel_anestesia
                + e.importe_estudio_cobrado
                + e.importe_medicacion_cobrado
                # - e.diferencia_paciente
                for e in presentacion.estudios.all()])
            pago = PagoPresentacionSerializer(data={
                "fecha": date.today(),
                "presentacion": presentacion.pk,
                "nro_recibo": request.data.get('nro_recibo'),
                "retencion_impositiva": Decimal(request.data.get('retencion_impositiva')),
                "importe": presentacion.total
            })
            pago.is_valid(raise_exception=True)
            pago.save()
            presentacion.estado = Presentacion.COBRADO
            presentacion.comprobante.estado = Comprobante.COBRADO
            presentacion.comprobante.save()
            presentacion.save()
            diferencia_facturada = presentacion.total_facturado - presentacion.total
            response = JsonResponse({"diferencia_facturada": diferencia_facturada})
        except Presentacion.DoesNotExist:
                response = JsonResponse({'error': "No existe una presentacion con esa id"}, status=400)
        except Estudio.DoesNotExist:
                response = JsonResponse({'error': "No existe un estudio con esa id"}, status=400)
        except ValidationError as ex:
            response = JsonResponse({'error': ex.message}, status=400)
        except Exception as ex:
            response = JsonResponse({'error': ex.message}, status=500)
        return response