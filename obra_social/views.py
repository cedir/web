from django.http import HttpResponse
from rest_framework import filters
from rest_framework import viewsets, generics
from estudio.models import ObraSocial
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
