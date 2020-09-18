from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, filters
from django.template import loader
from paciente.models import Paciente
from .models import Paciente
from .serializers import PacienteSerializer, PacienteFormSerializer


def create_form(request):
    # session check
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    c = {
        'isCreate': 1,
        'logged_user_name': request.user.username,
    }

    t = loader.get_template('turnos/ABMPaciente.html')
    return HttpResponse(t.render(c))


def update_form(request, id_paciente):
    # session check
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    paciente = get_object_or_404(Paciente, pk=id_paciente)

    fecha_nacimiento = ""
    if paciente.fechaNacimiento:
        fecha_nacimiento = paciente.fechaNacimiento.strftime(settings.FORMAT_DATE)

    c = {
        'id': paciente.id,
        'dni': paciente.dni,
        'nombre': paciente.nombre,
        'apellido': paciente.apellido,
        'domicilio': paciente.domicilio,
        'telefono': paciente.telefono,
        'fecha_nacimiento': fecha_nacimiento,
        'sexo': paciente.sexo,
        'nro_afiliado': paciente.nroAfiliado,
        'informacion_extra': paciente.informacion_extra or '',
        'email': paciente.email or '',
        'logged_user_name': request.user.username,
    }

    t = loader.get_template('turnos/ABMPaciente.html')
    return HttpResponse(t.render(c))


def buscar_form(request):
    # session check
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    cond = {}

    apellido = request.GET.get('apellido', '')
    if apellido:
        cond["apellido__icontains"] = apellido

    nombre = request.GET.get('nombre', '')
    if nombre:
        cond["nombre__icontains"] = nombre

    dni = request.GET.get('dni', '')
    if dni:
        cond["dni"] = dni

    request_type = request.GET.get('request_type')

    pacientes = Paciente.objects.filter(**cond).order_by("apellido", "nombre")[:75]

    arr_hsh_pacientes = [{
        "id": paciente.id,
        "dni": paciente.dni,
        "nombre": paciente.nombre,
        "apellido": paciente.apellido,
        "domicilio": paciente.domicilio or "",
        "telefono": paciente.telefono,
        "nro_afiliado": paciente.nroAfiliado,
        "email": paciente.email
    } for paciente in pacientes]

    c = {
        'logged_user_name': request.user.username,
        'pacientes': arr_hsh_pacientes,
        'apellido': apellido,
        'dni': dni,
    }

    template_name = 'turnos/buscarPaciente.html'
    if request_type == 'ajax':
        template_name = 'turnos/buscarPacienteAjax.html'

    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))


def create(request):
    paciente = PacienteFormSerializer(data = request.POST)
    response_dict = {
        'status': 1,
        'message': 'El paciente se ha creado correctamente.'
    }

    if paciente.is_valid():
        paciente.save()
        response_dict['idPaciente'] = paciente['id'].value
    else:
        response_dict = {'status': 0, 'message': paciente.errors[next(iter(paciente.errors))]}

    return JsonResponse(response_dict)

def update(request, id_paciente):
    paciente = PacienteFormSerializer(Paciente.objects.get(pk=id_paciente), data = request.POST)

    response_dict = {
        'status': 1,
        'message': 'El paciente se ha actualizado correctamente.'
    }

    if paciente.is_valid():
        paciente.save()
    else:
        response_dict = {'status': 0, 'message': paciente.errors[next(iter(paciente.errors))]}

    return JsonResponse(response_dict)

class PacienteNombreApellidoODniFilterBackend(filters.BaseFilterBackend):
    
    """
    Filtro de pacientes por nombre o apellido
    """
    def filter_queryset(self, request, queryset, view):
        search_text = request.query_params.get('search_text')


        if search_text:
            if str.isdigit(search_text):
                queryset = queryset.filter(Q(dni__icontains=search_text))
            else:
                search_params = [x.strip() for x in search_text.split(',')]
                nomOApe1 = search_params[0]
                nomOApe2 = search_params[1] if len(search_params) >= 2 else ''
                queryset = queryset.filter((Q(nombre__icontains=nomOApe1) & Q(apellido__icontains=nomOApe2)) |
                    (Q(nombre__icontains=nomOApe2) & Q(apellido__icontains=nomOApe1)))
        return queryset

class PacienteViewSet(viewsets.ModelViewSet):
    model = Paciente
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    filter_backends = (PacienteNombreApellidoODniFilterBackend, )
    pagination_class = None
