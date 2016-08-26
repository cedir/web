from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.template import Context, loader
from paciente.models import Paciente
from datetime import datetime
import simplejson


def get_create(request):
    # session check
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    c = Context({
        'isCreate': 1,
        'logged_user_name': request.user.username,
    })

    t = loader.get_template('turnos/ABMPaciente.html')
    return HttpResponse(t.render(c))


def get_update(request, id_paciente):
    # session check
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    paciente = get_object_or_404(Paciente, pk=id_paciente)

    fecha_nacimiento = ""
    if paciente.fechaNacimiento:
        fecha_nacimiento = paciente.fechaNacimiento.strftime(settings.FORMAT_DATE)

    c = Context({
        u'id': paciente.id,
        u'dni': paciente.dni,
        u'nombre': paciente.nombre,
        u'apellido': paciente.apellido,
        u'domicilio': paciente.domicilio,
        u'telefono': paciente.telefono,
        u'fecha_nacimiento': fecha_nacimiento,
        u'sexo': paciente.sexo,
        u'nro_afiliado': paciente.nroAfiliado,
        u'email': paciente.email or u'',
        u'logged_user_name': request.user.username,
    })

    t = loader.get_template('turnos/ABMPaciente.html')
    return HttpResponse(t.render(c))


def get_buscar(request):
    # session check
    if not request.user.is_authenticated():
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

    c = Context({
        'logged_user_name': request.user.username,
        'pacientes': arr_hsh_pacientes,
        'apellido': apellido,
        'dni': dni,
    })

    template_name = u'turnos/buscarPaciente.html'
    if request_type == u'ajax':
        template_name = u'turnos/buscarPacienteAjax.html'

    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))


def post_create(request):
    domicilio = request.POST.get(u'domicilio', u'')
    sexo = request.POST.get(u'sexo', u'')
    dni = request.POST.get(u'dni')
    dni = int(dni) if dni else 0

    fecha_nacimiento = request.POST.get('fecha_nacimiento')
    if fecha_nacimiento:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, settings.FORMAT_DATE)

    if dni > 0:  # revisar que el DNI no este duplicado, a menos que sea 0
        pacientes = Paciente.objects.filter(dni=dni)
        if pacientes:
            response_dict = {'status': 0, 'message': "Error, ya existe un paciente con DNI " + str(dni)}
            return HttpResponse(simplejson.dumps(response_dict))

    try:
        paciente = Paciente()
        paciente.nombre = request.POST['nombre']
        paciente.apellido = request.POST['apellido']
        paciente.dni = dni
        paciente.domicilio = domicilio
        paciente.telefono = request.POST['telefono']
        paciente.sexo = sexo
        paciente.fechaNacimiento = fecha_nacimiento
        paciente.nroAfiliado = request.POST.get(u'nro_afiliado', u'')
        paciente.email = request.POST.get(u'email')
        paciente.save(force_insert=True)

        response_dict = {
            'idPaciente': paciente.id,
            'status': 1,
            'message': "El paciente se ha creado correctamente."
        }
        return HttpResponse(simplejson.dumps(response_dict))

    except Exception:
        response_dict = {'status': 0, 'message': "Ocurrio un error. Revise los datos y vuelva a intentarlo."}
        return HttpResponse(simplejson.dumps(response_dict))


def post_update(request, id_paciente):
    domicilio = request.POST.get(u'domicilio', u'')
    sexo = request.POST.get(u'sexo', u'')
    dni = request.POST.get(u'dni')
    dni = int(dni) if dni else 0

    paciente = get_object_or_404(Paciente, pk=id_paciente)

    fecha_nacimiento = request.POST.get('fecha_nacimiento')
    if fecha_nacimiento:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, settings.FORMAT_DATE)

    if dni > 0:  # revisar que el DNI no este duplicado, a menos que sea 0
        pacientes = Paciente.objects.filter(dni=dni).exclude(id=paciente.id)
        if len(pacientes):
            response_dict = {'status': 0, 'message': "Error, ya existe un paciente con DNI " + str(dni)}
            return HttpResponse(simplejson.dumps(response_dict))

    try:
        paciente.dni = dni
        paciente.nombre = request.POST['nombre']
        paciente.apellido = request.POST['apellido']
        paciente.domicilio = domicilio
        paciente.telefono = request.POST['telefono']
        paciente.sexo = sexo
        paciente.fechaNacimiento = fecha_nacimiento
        paciente.nroAfiliado = request.POST.get(u'nro_afiliado', u'')
        paciente.email = request.POST.get(u'email')
        paciente.save()

        response_dict = {'status': 1, 'message': "El paciente se ha modificado correctamente."}
        return HttpResponse(simplejson.dumps(response_dict))

    except Exception as err:
        response_dict = {
            'status': 0,
            'message': "Ocurrio un error. Revise los datos y vuelva a intentarlo." + "Error:" + str(err)
        }
        return HttpResponse(simplejson.dumps(response_dict))
