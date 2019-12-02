import simplejson
from django.http import HttpResponse
from rest_framework import filters, viewsets, generics
from rest_framework.decorators import detail_route
from estudio.models import Estudio
from obra_social.models import ObraSocial
from estudio.serializers import EstudioDePresetancionSerializer
from obra_social.serializers import ObraSocialSerializer

class ObraSocialNombreFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de obra social por nombre
    """
    def filter_queryset(self, request, queryset, view):
        nombre = request.query_params.get(u'nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

            return queryset

# Create your views here.
class ObraSocialViewSet(viewsets.ModelViewSet):
    model = ObraSocial
    queryset = ObraSocial.objects.all()
    serializer_class = ObraSocialSerializer
    filter_backends = (ObraSocialNombreFilterBackend, )
    pagination_class = None

    @detail_route(methods=['get'])
    def estudios_sin_presentar(self, request, pk=None):
        estudios = Estudio.objects.filter(
            obra_social__pk=pk,
            presentacion__pk=0,
            es_pago_contra_factura=0,
        ).order_by('fecha', 'id')
        try:
            response = HttpResponse(simplejson.dumps([
                EstudioDePresetancionSerializer(estudio).data
                for estudio in estudios
            ]), content_type='application/json')
        except Exception as ex:
            response = HttpResponse(simplejson.dumps({'error': ex.message}), status=500, content_type='application/json')
        return response
