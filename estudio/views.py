import django_filters
from django.http import HttpResponse
from rest_framework import filters
from rest_framework import viewsets, generics
from estudio.models import Estudio
from estudio.serializers import EstudioSerializer
from imprimir import generar_informe

def imprimir(request, id_estudio):

    estudio = Estudio.objects.get(pk=id_estudio)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="Estudio de {0}.pdf"'.format(estudio.paciente.apellido)

    return generar_informe(response, estudio)


class EstudioPacienteFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de estudios por paciente
    """
    def filter_queryset(self, request, queryset, view):
        apellido = request.query_params.get(u'paciente_apellido')
        nombre = request.query_params.get(u'paciente_nombre')
        paciente_id = request.query_params.get(u'paciente_id')
        if apellido:
            queryset = queryset.filter(paciente__apellido__icontains=apellido)
        if nombre:
            queryset = queryset.filter(paciente__nombre__icontains=nombre)
        if paciente_id:
            queryset = queryset.filter(paciente_id=paciente_id)
        return queryset


class EstudioFechaFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de estudios por fecha
    """
    def filter_queryset(self, request, queryset, view):
        fecha = request.query_params.get(u'fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        return queryset

#class EstudioFilter(django_filters.FilterSet):
#    fecha_desde = django_filters.DateFilter(name="fecha", lookup_expr='gte')
#    fecha_hasta = django_filters.DateFilter(name="fecha", lookup_expr='lte')
#    class Meta:
#        model = Estudio
#        fields = [u'fecha', u'paciente', u'practica', u'obra_social', u'medico', u'medico_solicitante', u'fecha_desde', u'fecha_hasta']


class EstudioViewSet(viewsets.ModelViewSet):
    model = Estudio
    queryset = Estudio.objects.all()[:20]
    serializer_class = EstudioSerializer
    filter_backends = (EstudioPacienteFilterBackend, EstudioFechaFilterBackend, )
    #filter_class = EstudioFilter

