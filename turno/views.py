# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date

from django.core.exceptions import ValidationError
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponse, QueryDict, JsonResponse
from django.conf import settings
from django.template import loader
from django.utils.dateparse import parse_date
from rest_framework import viewsets

from estudio.models import Estudio
from medico.models import Medico, Disponibilidad
from obra_social.models import ObraSocial
from paciente.models import Paciente
from practica.models import Practica
from sala.models import Sala
from turno.models import InfoTurno
from turno.models import Turno, Estado, PeriodoSinAtencion
from turno.serializers import InfoTurnoSerializer, TurnoSerializer
from rest_framework.decorators import list_route
from security.encryption import encode
from common.drf.views import StandardResultsSetPagination
from common.utils import add_log_entry


PIXELS_PER_MINUTE = 1.333
err_ses = 'Error, la sesión se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo.'
spaDayNumbers = dict(lunes=0, martes=1, miercoles=2, jueves=3, viernes=4, sabado=5, domingo=6)
spaDays = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
spaMonths = [None, 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'setiembre',
             'octubre', 'noviembre', 'diciembre']


def get_home(request):
    # session check
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    c = {
        'logged_user_name': request.user.username,
    }
    t = loader.get_template('turnos/home.html')
    return HttpResponse(t.render(c))


def get_buscar_turnos(request):
    # session check
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    cond = {}

    paciente = request.GET.get('paciente', "")
    if paciente:
        cond["paciente__apellido__icontains"] = paciente

    fecha = request.GET.get('fecha', "")
    if fecha:
        if "/" in fecha:
            fecha = fecha.replace(" ", "")
            fecha = fecha.split("/")[2] + "-" + fecha.split("/")[1] + "-" + fecha.split("/")[0]
        cond["fechaTurno"] = fecha

    id_medico = request.GET.get('id-medico') or 0
    if id_medico:
        cond["medico__id"] = id_medico

    id_sala = request.GET.get('id-sala') or 0
    if id_sala:
        cond["sala__id"] = id_sala

    ocultar_anulados = request.GET.get('ocultar-turnos-anulados', "false")
    if ocultar_anulados == "true":
        cond["estado__id__lte"] = 2

    rows_limit = 110

    # default filter if its empty
    if not list(cond.keys()):
        rows_limit = 50

    arr_turnos = Turno.objects.filter(**cond).order_by("-fechaTurno", 'horaInicio')[:rows_limit]
    medicos = Medico.objects.all().order_by("apellido")
    obra_sociales = ObraSocial.objects.all().order_by('nombre')
    salas = Sala.objects.all().order_by('id')

    arr_hsh_turnos = [{
        "id": turno.id,
        "nombre": turno.paciente.nombre,
        "apellido": turno.paciente.apellido,
        "id_paciente": turno.paciente.id,
        "dni_paciente": turno.paciente.dni,
        "fecha": _sql_date_to_normal_date(turno.fechaTurno),
        "hora_inicio": turno.horaInicio,
        "medico": turno.medico.apellido + ", " + turno.medico.nombre,
        "obra_social": turno.obraSocial.nombre,
        "observacion": turno.observacion,
        "img_estado": turno.estado.img,
        "practica": " - ".join([practica.__str__() for practica in turno.practicas.all()])
    } for turno in arr_turnos]

    arr_medicos = [{
       "id": medico.id,
       "nombre": medico.nombre,
       "apellido": medico.apellido,
       "selected": 1 if medico.id == int(id_medico) else 0
    } for medico in medicos]

    arr_salas = [{
        "id": sala.id,
        "nombre": sala.nombre,
        "selected": 1 if sala.id == int(id_sala) else 0
    } for sala in salas]

    arr_obras_sociales = [{
        "id": medico.id,
        "nombre": medico.nombre
    } for medico in obra_sociales]

    c = {
        'turnos': arr_hsh_turnos,
        'medicos': arr_medicos,
        'fecha': _sql_date_to_normal_date(fecha),
        'obrasSociales': arr_obras_sociales,
        'salas': arr_salas,
        'paciente': paciente,
        'ocultarAnuladosState': 'checked' if ocultar_anulados == 'true' else '',
        'logged_user_name': request.user.username,
        'uli_url': settings.ULI_URL
    }

    t = loader.get_template('turnos/buscarTurnos.html')

    return HttpResponse(t.render(c))


def get_turno(request, id_turno):

    try:
        turno = Turno.objects.get(id=id_turno)
    except Turno.DoesNotExist:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        return JsonResponse(response_dict)

    ct = ContentType.objects.get_for_model(Turno)

    # TODO: traer logs en una llamada sola, y mostrarlos todos (tambien los anulados, confirmados, etc.)
    created_log = LogEntry.objects.filter(content_type_id=ct.id, action_flag=ADDITION, object_id=id_turno)
    last_modified_log = LogEntry.objects.filter(content_type_id=ct.id, action_flag=CHANGE, object_id=id_turno)

    response_dict = {
        "id": turno.id,
        "fecha": turno.fechaTurno.strftime(settings.FORMAT_DATE),
        "paciente": turno.paciente.apellido + ", " + turno.paciente.nombre,
        "tel": turno.paciente.telefono,
        "dni": turno.paciente.dni,
        "paciente_id": turno.paciente.id,
        "hora_inicio": str(turno.horaInicio),
        "hora_fin_real": str(turno.horaFinReal),
        "hora_fin": str(turno.horaFinEstimada),
        "observacion": turno.observacion,
        "fecha_otorgamiento": turno.fecha_otorgamiento.strftime(settings.FORMAT_DATETIME),
        "fecha_ult_mod": last_modified_log[0].action_time.strftime(settings.FORMAT_DATETIME) if last_modified_log else '-',
        "medico": turno.medico.apellido + ", " + turno.medico.nombre,
        "obra_social": turno.obraSocial.id,
        "obra_social_nombre": turno.obraSocial.nombre,
        "sala": turno.sala.nombre,
        "estado": turno.estado.descripcion,
        "creado_por": created_log[0].user.username if created_log else '-no disponible-',
        "ult_mod_por": last_modified_log[0].user.username if last_modified_log else '-no disponible-',
        "motivo_ult_mod": last_modified_log[0].change_message if last_modified_log else '-',
        "practicas": ' - '.join([p.__str__() for p in turno.practicas.all()])
        # TODO: registrar el usuario que anula el turno y una observación al respecto
        # "anulado_por": ...
        # observacion_anulacion": ...
    }

    return JsonResponse(response_dict)


def get_turnos_disponibles(request):
    # session check
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    return _get_turnos_disponibles(request.user, request.GET)


def get_next_day_line(request):
    fecha = request.GET['fecha']
    id_sala = request.GET['id-sala'] or 0
    id_medico = request.GET.get('id-medico') or 0
    sp = fecha.split('-')
    c = date(int(sp[0]), int(sp[1]), int(sp[2]))
    next_date = _get_next_day(c, id_sala, id_medico)
    day_lines = _get_day_line(next_date, id_sala)
    return HttpResponse(day_lines)


def get_back_day_line(request):
    fecha = request.GET['fecha']
    id_sala = request.GET['id-sala'] or 0
    id_medico = request.GET.get('id-medico') or 0
    sp = fecha.split('-')
    c = date(int(sp[0]), int(sp[1]), int(sp[2]))
    back_date = _get_previous_day(c, id_sala, id_medico)
    day_lines = _get_day_line(back_date, id_sala)
    return HttpResponse(day_lines)


def guardar(request):
    err_sup = 'Error, se ha detectado superposición de turnos. Por favor, haga click en Mostrar y vuelva a intentarlo.'
    # session check
    if not request.user.is_authenticated:
        response_dict = {'status': 0, 'message': err_ses}
        return JsonResponse(response_dict)

    hora_inicio = request.GET['hora_inicio']
    hora_fin_estimada = request.GET['hora_fin_estimada']
    fecha_turno = parse_date(request.GET['fecha_turno'])
    id_sala = request.GET['id-sala']

    # gte...>=  -  lte...<=  -  gt....>  -  lt....<
    arr_turnos = Turno.objects.filter(
        Q(fechaTurno=fecha_turno, sala__id=id_sala, estado__id__lt=3),
        Q(horaInicio__lte=hora_inicio, horaFinEstimada__gt=hora_inicio)
        |
        Q(horaInicio__lt=hora_fin_estimada, horaFinEstimada__gte=hora_fin_estimada)
    )

    if len(arr_turnos) > 0:
        response_dict = {'status': 0, 'message': err_sup}
        return JsonResponse(response_dict)


    id_paciente = request.GET['id-paciente']
    id_practicas = request.GET.getlist('id-practicas[]')
    id_medico = request.GET['id-medico']
    id_obra_social = request.GET['id-obra-social']
    observacion_turno = request.GET['observacion_turno']

    if (_is_feriado(fecha_turno) or _is_medico_con_licencia(fecha_turno, id_medico)):
        err_no_atiende = 'El medico no atiende en la fecha seleccionada'
        response_dict = {'status': 0, 'message': err_no_atiende}
        return JsonResponse(response_dict)

    try:
        paciente = Paciente.objects.get(id=id_paciente)
        practicas = Practica.objects.filter(id__in=id_practicas)
        turno = Turno()
        turno.horaInicio = hora_inicio
        turno.horaFinEstimada = hora_fin_estimada
        turno.horaFinReal = hora_fin_estimada
        turno.fecha_otorgamiento = datetime.now()
        turno.fechaTurno = fecha_turno
        turno.observacion = observacion_turno
        turno.paciente = paciente
        turno.medico_id = id_medico
        turno.obraSocial_id = id_obra_social
        turno.sala_id = id_sala
        turno.estado_id = 1
        turno.save(force_insert=True)

        for practica in practicas:
            turno.practicas.add(practica)

        turno.save()

        add_log_entry(turno, request.user, ADDITION, 'CREA')

        response_dict = {'status': 1, 'message': "El turno se ha creado correctamente."}
        return JsonResponse(response_dict)

    except Paciente.DoesNotExist:
        response_dict = {'status': 0, 'message': "Error, no existe el paciente"}
        return JsonResponse(response_dict)
    except Exception as err:
        response_dict = {'status': 0, 'message': str(err)}
        return JsonResponse(response_dict)


def update(request, id_turno):
    # session check
    if not request.user.is_authenticated:
        response_dict = {'status': 0, 'message': err_ses}
        return JsonResponse(response_dict)

    id_obra_social = request.GET['id-obra-social']
    observacion = request.GET['observacion']

    try:
        turno = Turno.objects.get(id=id_turno)

        if turno.estado.id == Estado.ANULADO:
            raise ValidationError('El turno esta anulado y no acepta modificaciones')

        turno.obraSocial = ObraSocial.objects.get(id=id_obra_social)
        turno.observacion = observacion
        turno.save()

        add_log_entry(turno, request.user, CHANGE, "MODIFICA")

        response_dict = {'status': 1, 'message': "El turno se ha guardado correctamente."}
        return JsonResponse(response_dict)

    except Turno.DoesNotExist:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        return JsonResponse(response_dict)
    except ValidationError as e:
        response_dict = {'status': 0, 'message': e.message}
        return JsonResponse(response_dict)
    except Exception as err:
        return str(err)


def anunciar(request, id_turno):
    if not request.user.is_authenticated:
        response_dict = {'status': 0, 'message': err_ses}
        return JsonResponse(response_dict)

    try:
        turno = Turno.objects.get(id=id_turno)

        if turno.estado.id == Estado.ANULADO:
            raise ValidationError('El turno esta anulado y no acepta modificaciones')

        practicas = turno.practicas.all()
        for practica in practicas:
            estudio = Estudio()
            estudio.paciente_id = turno.paciente.id
            estudio.practica_id = practica.id
            estudio.fecha = turno.fechaTurno
            estudio.medico_id = turno.medico.id
            estudio.obra_social_id = turno.obraSocial.id
            estudio.medico_solicitante_id = turno.medico.id
            estudio.nro_de_orden = ""
            estudio.anestesista_id = 1
            estudio.set_create_defaults()
            estudio.save()

            # log estudio
            add_log_entry(estudio, request.user, ADDITION, 'CREA (desde turnos)')

        add_log_entry(turno, request.user, CHANGE, "ANUNCIA")

        response_dict = {'status': True, 'message': "Success"}
        return JsonResponse(response_dict)

    except Turno.DoesNotExist:
        response_dict = {'status': False, 'message': "Error, no existe turno"}
        return JsonResponse(response_dict)
    except ValidationError as e:
        response_dict = {'status': 0, 'message': e.message}
        return JsonResponse(response_dict)
    except Exception as err:
        response_dict = {'status': False, 'message': str(err)}
        return JsonResponse(response_dict)


def anular(request, id_turno):
    if not request.user.is_authenticated:
        response_dict = {'status': 0, 'message': err_ses}
        return JsonResponse(response_dict)

    observacion_turno = request.GET['observacion_turno']

    try:
        turno = Turno.objects.get(id=id_turno)

        if turno.estado.id == Estado.ANULADO:
            raise ValidationError('El turno esta anulado y no acepta modificaciones')

        turno.estado = Estado.objects.get(id=Estado.ANULADO)

        if observacion_turno:
            turno.observacion = observacion_turno

        turno.save()

        add_log_entry(turno, request.user, CHANGE, "ANULA")

        response_dict = {'status': 1, 'message': "El turno se ha anulado correctamente."}
        return JsonResponse(response_dict)

    except Turno.DoesNotExist:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        return JsonResponse(response_dict)
    except ValidationError as e:
        response_dict = {'status': 0, 'message': e.message}
        return JsonResponse(response_dict)
    except Exception as err:
        return str(err)


def reprogramar(request, id_turno):
    if not request.user.is_authenticated:
        response_dict = {'status': 0, 'message': err_ses}
        return JsonResponse(response_dict)

    observacion_turno = request.GET['observacion_turno']

    try:
        turno = Turno.objects.get(id=id_turno)

        if turno.estado.id != Estado.ANULADO:
            turno.estado = Estado.objects.get(id=Estado.ANULADO)
            if observacion_turno:
                turno.observacion = observacion_turno
            turno.save()

            add_log_entry(turno, request.user, CHANGE, "REPROGRAMA")

        practicas = turno.practicas.all()

        # generamos una estructura de datos similar a request.GET
        data = QueryDict('', mutable=True)
        data.update({
            'id-sala': turno.sala.id,
            'id-paciente': turno.paciente.id,
            'id-medico': turno.medico.id,
            'id-obra-social': turno.obraSocial.id
        })
        data.setlist('id-practicas[]', [str(practica.id) for practica in practicas])

        return _get_turnos_disponibles(request.user, data)

    except Turno.DoesNotExist:
        return get_buscar_turnos(request)
    except Exception as err:
        return str(err)


def confirmar(request, id_turno):
    if not request.user.is_authenticated:
        response_dict = {'status': 0, 'message': err_ses}
        return JsonResponse(response_dict)

    try:
        turno = Turno.objects.get(id=id_turno)

        if turno.estado.id == Estado.ANULADO:
            raise ValidationError('El turno esta anulado y no acepta modificaciones')

        turno.estado = Estado.objects.get(id=Estado.CONFIRMADO)
        turno.save()
        add_log_entry(turno, request.user, CHANGE, "CONFIRMA")

        response_dict = {'status': 1, 'message': "El turno se ha confirmado correctamente."}
        return JsonResponse(response_dict)

    except Turno.DoesNotExist:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        return JsonResponse(response_dict)
    except ValidationError as e:
        response_dict = {'status': 0, 'message': e.message}
        return JsonResponse(response_dict)
    except Exception as err:
        return str(err)


def _is_feriado(fecha):
    return PeriodoSinAtencion.objects.filter(medico__isnull=True, fecha_inicio__lte=fecha, fecha_fin__gte=fecha).exists()


def _is_medico_con_licencia(fecha, id_medico):
    return PeriodoSinAtencion.objects.filter(medico_id=id_medico, fecha_fin__gte=fecha, fecha_inicio__lte=fecha).exists()


def _get_day_line(fecha, id_sala):
    """
    Arma la linea de tiempo con los turnos existentes y la disponibilidad de los medicos (hora en los que atienden)
    para el dia y la sala dada.
    :param fecha: fecha en formato String
    :param id_sala: Int id de sala.
    :return: HTML object con la linea de tiempo
    """

    dia = spaDays[fecha.weekday()]
    mes = spaMonths[fecha.month]

    fecha_format = str(fecha)
    dia_format = dia + ' ' + str(fecha.day) + ' de ' + mes + ' del ' + str(fecha.year)
    turnos = Turno.objects.filter(fechaTurno=fecha, sala__id=int(id_sala), estado__id__lt=3)
    disponibilidades = Disponibilidad.objects.filter(dia=dia, sala__id=id_sala, fecha__lte=date.today())\
        .order_by('horaInicio')
    colors = ('#71FF86', '#fffccc', '#A6C4FF')
    day_line_template = loader.get_template('turnos/dayLine.html')

    arr_hsh_turnos = [{
          "id": turno.id,
          "paciente": turno.paciente.nombre + ' ' + turno.paciente.apellido,
          "top": (((turno.horaInicio.hour - 7) * 60) + turno.horaInicio.minute) * PIXELS_PER_MINUTE + 11,
          "fecha": turno.fechaTurno,
          "hora": turno.horaInicio,
          "duracion": turno.getDuracionEnMinutos(),
          "duracionEnPixeles": turno.getDuracionEnMinutos() * PIXELS_PER_MINUTE - (1 * PIXELS_PER_MINUTE),
          "medico": turno.medico.nombre + ' ' + turno.medico.apellido,
          "obra_social": turno.obraSocial.nombre,
          "practicas": '-'.join([p.__str__() for p in turno.practicas.all()])
      } for turno in turnos]

    arr_hsh_disponibilidad = [{
          "id": disp.id, 
          "top": (((disp.horaInicio.hour - 7) * 60) + disp.horaInicio.minute) * PIXELS_PER_MINUTE + 9,
          "fecha": disp.fecha,
          "hora": disp.horaInicio,
          "duracionEnPixeles": disp.getDuracionEnMinutos() * PIXELS_PER_MINUTE,
          "medico": " ".join(list(disp.medico.apellido)),
          "color": 'red' if _is_medico_con_licencia(fecha, disp.medico_id) else colors[index % 3],
          "sala": disp.sala.nombre
      } for (index, disp) in enumerate(disponibilidades)]

    day_line_context = {
        'lineDay': dia_format,
        'fechaTurno': fecha_format,
        'turnos': arr_hsh_turnos,
        'disponibilidades': arr_hsh_disponibilidad,
        'feriado': _is_feriado(fecha),
    }

    return day_line_template.render(day_line_context)


def _get_next_day(cur_date, id_sala, id_medico=None):
    if id_medico == 0:
        return cur_date + timedelta(days=1)

    disponibilidades = Disponibilidad.objects.filter(medico__id=id_medico, sala__id=id_sala)
    if not disponibilidades.count():
        return cur_date + timedelta(days=1)

    hsh_disponibilidades = {}
    for disp in disponibilidades:
        hsh_disponibilidades[spaDayNumbers[disp.dia]] = disp.horaInicio

    cur_day = cur_date.weekday()

    for i in range(1, 8):
        if (cur_day + i) % 7 in hsh_disponibilidades:
            return cur_date + timedelta(days=i)

    return cur_date + timedelta(days=1)


def _get_previous_day(curr_date, id_sala, id_medico=None):
    if id_medico == 0:
        return curr_date - timedelta(days=1)

    disponibilidades = Disponibilidad.objects.filter(medico__id=id_medico, sala__id=id_sala)
    if not disponibilidades.count():
        return curr_date - timedelta(days=1)

    hsh_disponibilidades = {}
    for disp in disponibilidades:
        hsh_disponibilidades[spaDayNumbers[disp.dia]] = disp.horaInicio

    cur_day = curr_date.weekday()
    for i in range(1, 8):
        if (cur_day - i) % 7 in hsh_disponibilidades:
            return curr_date - timedelta(days=i)

    return curr_date - timedelta(days=1)


def _get_turnos_disponibles(user, data):
    id_paciente = data.get('id-paciente')
    id_sala = data.get('id-sala') or 0
    id_medico = data.get('id-medico') or 0
    id_obra_social = data.get('id-obra-social') or 0
    id_practicas = data.getlist('id-practicas[]') or []
    fecha = data.get('fecha', "")

    medicos = Medico.objects.all().order_by("apellido")
    obra_sociales = ObraSocial.objects.all().order_by('nombre')
    practicas = Practica.objects.all().order_by('-usedLevel', 'descripcion')
    salas = Sala.objects.all().order_by('id')

    try:
        paciente_seleccionado = Paciente.objects.get(id=id_paciente) if id_paciente else None
    except Paciente.DoesNotExist:
        paciente_seleccionado = None

    selected_date = date(int(fecha.split("/")[2]), int(fecha.split("/")[1]), int(fecha.split("/")[0]))\
        if fecha else date.today()

    selected_date = selected_date - timedelta(days=1)  # resto uno ya que nextDay le va a sumar uno luego

    day_lines = []
    if id_sala:
        # estudiar si los arreglos se estan devolviendo por referencia y llamar aca a _get_day_line q hace exact.
        # lo mismo que este codigo
        for i in range(0, 4):
            next_date = _get_next_day(selected_date, id_sala, id_medico)
            line = _get_day_line(next_date, id_sala)
            selected_date = next_date
            day_lines.append(line)

    arr_medicos = [{
        "id": medico.id,
        "nombre": medico.nombre,
        "apellido": medico.apellido,
        "selected": 1 if medico.id == int(id_medico) else 0
    } for medico in medicos]

    arr_salas = [{
        "id": sala.id,
        "nombre": sala.nombre,
        "selected": 1 if sala.id == int(id_sala) else 0
    } for sala in salas]

    arr_obras_sociales = [{
        "id": medico.id,
        "nombre": medico.nombre,
        "selected": 1 if medico.id == int(id_obra_social) else 0
    } for medico in obra_sociales]

    arr_practicas = [{
        "id": practica.id,
        "nombre": practica.descripcion,
        "selected": 1 if str(practica.id) in id_practicas else 0
    } for practica in practicas]

    c = {
        'dayLines': day_lines,
        'nombrePaciente': paciente_seleccionado.nombre if paciente_seleccionado else "",
        'apellidoPaciente': paciente_seleccionado.apellido if paciente_seleccionado else "",
        'idPaciente': paciente_seleccionado.id if paciente_seleccionado else "",
        'showLines': bool(day_lines),
        'medicos': arr_medicos,
        'obrasSociales': arr_obras_sociales,
        'practicas': arr_practicas,
        'salas': arr_salas,
        'fecha': fecha,
        'logged_user_name': user.username,
    }

    t = loader.get_template('turnos/buscarTurnosDisponibles.html')

    return HttpResponse(t.render(c))


def _sql_date_to_normal_date(date_time):
    if str(date_time) == "":
        return ""
    try:
        arr = str(date_time).split(" ")
        arr2 = arr[0].split("-")
        time = ""
        if len(arr) > 1:
            time = arr[1]
        return arr2[2] + "/" + arr2[1] + "/" + arr2[0] + " " + time
    except Exception:
        return str(date_time)


class InfoTurnoViewSet(viewsets.ModelViewSet):
    model = InfoTurno
    queryset = InfoTurno.objects.all()
    serializer_class = InfoTurnoSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = InfoTurno.objects.all()
        medico_id = self.request.query_params.get('medico')
        practica_ids = self.request.query_params.get('practicas')
        obra_social_ids = self.request.query_params.get('obras_sociales')

        if medico_id:
            queryset = queryset.filter(Q(medico=medico_id) | Q(medico__isnull=True))

        if obra_social_ids:
            queryset = queryset.filter(
                Q(obra_sociales__id__in=obra_social_ids.split(','))
                |
                Q(obra_sociales__isnull=True)
            )

        if practica_ids:
            queryset = queryset.filter(Q(practicas__id__in=practica_ids.split(',')) | Q(practicas__isnull=True))

        return queryset.distinct()

class TurnoViewSet(viewsets.ModelViewSet):
    model = Turno
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    pagination_class = StandardResultsSetPagination

    @list_route(methods=['POST'])
    def contador_turnos(self, request):
        usuarios = request.data.get('usuarios', [])
        fechas = request.data.get('fechas', [])
        ct = ContentType.objects.get_for_model(Turno)
        turnos = LogEntry.objects.filter(content_type_id=ct.id, action_flag=ADDITION)

        cantidad_turnos = {}

        for usuario in usuarios:
            turnos_usuario = turnos.filter(user__username=usuario)

            cantidades = [
                    turnos_usuario.filter(action_time__gte=desde, action_time__lte=hasta).count()
                    for desde, hasta in fechas
                ]

            cantidad_turnos[usuario] = cantidades

        return JsonResponse(cantidad_turnos, status=200)
