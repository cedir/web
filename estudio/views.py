import django_filters
from django.http import HttpResponse
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


class EstudioFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(name="fecha", lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(name="fecha", lookup_expr='lte')
    class Meta:
        model = Estudio
        fields = [u'fecha', u'paciente', u'practica', u'obra_social', u'medico', u'medico_solicitante', u'fecha_desde', u'fecha_hasta']


class EstudioViewSet(viewsets.ModelViewSet):
    model = Estudio
    queryset = Estudio.objects.all()
    serializer_class = EstudioSerializer
    filter_class = EstudioFilter

