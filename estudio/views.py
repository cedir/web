from django.http import HttpResponse
from rest_framework import viewsets
from estudio.models import Estudio
from estudio.serializers import EstudioSerializer
from imprimir import generar_informe


def imprimir(request, id_estudio):

    estudio = Estudio.objects.get(pk=id_estudio)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="Estudio de {0}.pdf"'.format(estudio.paciente.apellido)

    return generar_informe(response, estudio)


class EstudioViewSet(viewsets.ModelViewSet):
    model = Estudio
    queryset = Estudio.objects.all()
    serializer_class = EstudioSerializer

