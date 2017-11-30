from django.http import HttpResponse
from rest_framework import filters
from rest_framework import viewsets, generics
from common.drf.views import StandardResultsSetPagination
from estudio.models import Estudio
from estudio.serializers import EstudioSerializer
from imprimir import generar_informe

def imprimir(request, id_estudio):

    estudio = Estudio.objects.get(pk=id_estudio)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="Estudio de {0}.pdf"'.format(estudio.paciente.apellido)

    return generar_informe(response, estudio)

class EstudioObraSocialFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de estudios por obra social
    """
    def filter_queryset(self, request, queryset, view):
        obra_social = request.query_params.get(u'obra_social')
        if obra_social:
            queryset = queryset.filter(obra_social__nombre__icontains=obra_social)
        return queryset

class EstudioMedicoFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de estudios por medico actuante
    """
    def filter_queryset(self, request, queryset, view):
        apellido = request.query_params.get(u'medico_apellido')
        nombre = request.query_params.get(u'medico_nombre')
        if apellido:
            queryset = queryset.filter(medico__apellido__icontains=apellido)
        if nombre:
            queryset = queryset.filter(medico__nombre__icontains=nombre)
        return queryset

class EstudioMedicoSolicitanteFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de estudios por medico solicitante
    """
    def filter_queryset(self, request, queryset, view):
        apellido = request.query_params.get(u'medico_solicitante_apellido')
        nombre = request.query_params.get(u'medico_solicitante_nombre')
        if apellido:
            queryset = queryset.filter(medico_solicitante__apellido__icontains=apellido)
        if nombre:
            queryset = queryset.filter(medico_solicitante__nombre__icontains=nombre)
        return queryset

class EstudioPacienteFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de estudios por paciente
    """
    def filter_queryset(self, request, queryset, view):
        dni = request.query_params.get(u'paciente_dni')
        apellido = request.query_params.get(u'paciente_apellido')
        nombre = request.query_params.get(u'paciente_nombre')
        paciente_id = request.query_params.get(u'paciente_id')
        if dni:
            queryset = queryset.filter(paciente__dni__icontains=dni)
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
        fecha_desde = request.query_params.get(u'fecha_desde')
        fecha_hasta = request.query_params.get(u'fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        return queryset

class EstudioViewSet(viewsets.ModelViewSet):
    model = Estudio
    queryset = Estudio.objects.all()
    serializer_class = EstudioSerializer
    filter_backends = (EstudioObraSocialFilterBackend, EstudioMedicoFilterBackend,
        EstudioMedicoSolicitanteFilterBackend, EstudioPacienteFilterBackend,
        EstudioFechaFilterBackend, )
    pagination_class = StandardResultsSetPagination
    page_size = 20
