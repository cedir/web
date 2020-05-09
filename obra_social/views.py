import simplejson
from django.http import JsonResponse
from rest_framework import filters, viewsets, generics
from rest_framework.decorators import detail_route
from estudio.models import Estudio
from obra_social.models import ObraSocial
from estudio.serializers import EstudioDePresetancionRetrieveSerializer
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
        # Un estudio no presentado en realidad deberia tener presentacion=NULL
        # El legacy le pone id=0
        # Como aca presentacion es FK (como corresponde), esto esta bastante DUDOSO por ahora y complica despues el serializer
        # Cuando el legacy arregle eso (o lo tiremos) esto deberia cambiar para buscar presentacion=None
        sucursal = request.query_params.get(u'sucursal', default='Cedir')
        estudios = Estudio.objects.filter(
            obra_social__pk=pk,
            es_pago_contra_factura=0,
            presentacion_id=0,
            fecha__year__gt=2017,
            sucursal=sucursal,
        ).order_by('fecha', 'id')
        try:
            response = JsonResponse(EstudioDePresetancionRetrieveSerializer(estudios, many=True).data, status=200, safe=False)
        except Exception as ex:
            response = JsonResponse({'error': ex.message}, status=500)
        return response
