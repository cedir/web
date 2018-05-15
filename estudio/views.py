from django.http import HttpResponse
from rest_framework import filters
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from common.drf.views import StandardResultsSetPagination
from estudio.models import Estudio
from estudio.models import Medicacion
from medicamento.models import Medicamento
from estudio.serializers import EstudioSerializer, EstudioCreateUpdateSerializer
from estudio.serializers import MedicacionSerializer, MedicacionCreateUpdateSerializer
from imprimir import generar_informe
import simplejson

def imprimir(request, id_estudio):

    estudio = Estudio.objects.get(pk=id_estudio)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="Estudio de {0}.pdf"'.format(estudio.paciente.apellido)

    return generar_informe(response, estudio)

def add_default_medicacion(request):

    id_estudio = request.POST['id_estudio']
    default_medicamentos_ids = (2, 3, 4, 5, 6, 7, 8, 22, 23, 35, 36, 37, 42, 48, 109, 128, 144, 167, 169)

    estudio = Estudio.objects.get(pk=id_estudio)

    for medicamento_id in default_medicamentos_ids:
        medicacion = Medicacion()
        medicacion.estudio = estudio
        medicacion.medicamento = Medicamento.objects.get(pk=medicamento_id)
        medicacion.importe = medicacion.medicamento.importe
        medicacion.save()
    
    response_dict = {
            'status': 200,
            'estudio': estudio.id,
            'message': "default medicacion added"
        }
    
    return HttpResponse(simplejson.dumps(response_dict))


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
        EstudioFechaFilterBackend, filters.OrderingFilter, )
    pagination_class = StandardResultsSetPagination
    ordering_fields = ('fecha', 'id')
    page_size = 20

    serializers = {
        'create': EstudioCreateUpdateSerializer,
        'update': EstudioCreateUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)

class MedicacionEstudioFilterBackend(filters.BaseFilterBackend):
    """
    Filtro de medicaciones por estudio
    """
    def filter_queryset(self, request, queryset, view):
        estudio = request.query_params.get(u'estudio')
        if estudio:
            queryset = queryset.filter(estudio__id=estudio)
        return queryset


class MedicacionViewSet(viewsets.ModelViewSet):
    model = Medicacion
    queryset = Medicacion.objects.all()
    serializer_class = MedicacionSerializer
    filter_backends = (MedicacionEstudioFilterBackend, )

    serializers = {
        'create': MedicacionCreateUpdateSerializer,
        'update': MedicacionCreateUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({ "estudio": instance.estudio.id })
    
    def perform_destroy(self, instance):
        instance.delete()