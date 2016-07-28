# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date

from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.dateparse import parse_date
from rest_framework import viewsets

from estudio.models import Estudio
from managers.models import AuditLog, Usuario
from managers.view.turnos import *
from medico.models import Medico, Disponibilidad
from obra_social.models import ObraSocial
from paciente.models import Paciente
from practica.models import Practica
from sala.models import Sala
from turno.models import InfoTurno
from turno.models import Turno, Estado
from turno.serializers import InfoTurnoSerializer
from utils.security import encode

spaDayNumbers = dict(lunes=0, martes=1, miercoles=2, jueves=3, viernes=4, sabado=5, domingo=6)
spaDays = [u'lunes', u'martes', u'miércoles', u'jueves', u'viernes', u'sábado', u'domingo']
spaMonths = [None, u'enero', u'febrero', u'marzo', u'abril', u'mayo', u'junio', u'julio', u'agosto', u'setiembre',
             u'octubre', u'noviembre', u'diciembre']


def get_buscar_turnos(request):
    # session check
    if request.session.get('cedir_user_id') is None:
        return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

    cond = {}

    paciente = ""
    if 'paciente' in request.GET and request.GET['paciente'] != "":
        paciente = request.GET['paciente']
        cond["paciente__apellido__icontains"] = paciente

    fecha = ""
    if 'fecha' in request.GET and request.GET['fecha'] != "":
        fecha = request.GET['fecha']
        if "/" in fecha:
            fecha = fecha.replace(" ", "")
            fecha = fecha.split("/")[2] + "-" + fecha.split("/")[1] + "-" + fecha.split("/")[0]
        cond["fechaTurno"] = fecha

    id_medico = 0
    if 'id-medico' in request.GET and request.GET['id-medico'] != "":
        id_medico = request.GET['id-medico']
        cond["medico__id"] = id_medico

    id_sala = 0
    if 'id-sala' in request.GET and request.GET['id-sala'] != "":
        id_sala = request.GET['id-sala']
        cond["sala__id"] = id_sala

    ocultar_anulados = request.GET.get('ocultar-turnos-anulados', "false")
    if ocultar_anulados == "true":
        cond["estado__id__lte"] = 2

    rows_limit = 110
    # default filter if its empty
    a = cond.keys()
    if len(a) == 0:
        rows_limit = 50

    arr_turnos = Turno.objects.filter(**cond).order_by("-fechaTurno", 'horaInicio')[:rows_limit]
    medicos = Medico.objects.all().order_by("apellido")
    obra_sociales = ObraSocial.objects.all().order_by('nombre')
    salas = Sala.objects.all().order_by('id')

    view_turnos = ViewTurnos(request)
    kwargs = {
        'turnos': arr_turnos, 'fecha': fecha, 'idMedico': id_medico, 'medicos': medicos,
        'obraSociales': obra_sociales, 'salas': salas, 'idSala': id_sala, 'paciente': paciente,
        'ocultarAnulados': ocultar_anulados
    }
    return HttpResponse(view_turnos.getBuscarTurnos(**kwargs))


def get_turno(request, id_turno):
    turno = Turno.objects.get(id=id_turno)
    created_log = AuditLog.objects.filter(objectId=int(id_turno), objectTypeId=3, userActionId=1)
    user = None
    if len(created_log) > 0:
        user = created_log[0].user.nombreUsuario

    view_turnos = ViewTurnos()
    kwargs = {'turno': turno, 'createdUser': user}
    return HttpResponse(view_turnos.getTurno(**kwargs))


def get_turnos_disponibles(request, **kwargs):
    # session check
    if request.session.get('cedir_user_id') is None:
        return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

    id_paciente = request.GET.get('id-paciente', kwargs.get('id-paciente')) or None
    id_sala = request.GET.get('id-sala', kwargs.get('id-sala')) or 0
    id_medico = request.GET.get('id-medico', kwargs.get('id-medico')) or 0
    id_obra_social = request.GET.get('id-obra-social', kwargs.get('id-obra-social')) or 0

    id_practicas = []
    if 'id-practicas[]' in request.GET and request.GET['id-practicas[]'] != "":
        id_practicas = request.GET.getlist('id-practicas[]')
    else:
        by_ref = kwargs.get('id-practicas[]', "")
        if by_ref != "":
            id_practicas = kwargs['id-practicas[]']

    fecha = ""
    if 'fecha' in request.GET and request.GET['fecha'] != "":
        fecha = request.GET['fecha']

    medicos = Medico.objects.all().order_by("apellido")
    obra_sociales = ObraSocial.objects.all().order_by('nombre')
    practicas = Practica.objects.all().order_by('-usedLevel', 'descripcion')
    salas = Sala.objects.all().order_by('id')

    paciente_seleccionado = None
    if id_paciente is not None:
        paciente_seleccionado = Paciente.objects.get(id=id_paciente)

    selected_date = date.today()
    if fecha != "":
        selected_date = date(int(fecha.split("/")[2]), int(fecha.split("/")[1]), int(fecha.split("/")[0]))

    selected_date = selected_date - timedelta(days=1)  # resto uno ya que nextDay le va a sumar uno luego

    day_lines = []
    if id_sala:
        # estudiar si los arreglos se estan devolviendo por referencia y llamar aca a _get_day_lines q hace exact.
        # lo mismo que este codigo
        for i in range(0, 4):
            next_date = _get_next_day(selected_date, id_sala, id_medico)
            line = _get_day_lines(next_date, id_sala)
            selected_date = next_date

            day_lines.append(line)

    view_turnos = ViewTurnos(request)
    kwargs = {'dayLines': day_lines, 'pacienteSeleccionado': paciente_seleccionado, 'idMedico': id_medico,
              'medicos': medicos, 'obraSociales': obra_sociales, 'idObraSocial': id_obra_social,
              'practicas': practicas, 'idPracticas': id_practicas, 'salas': salas, 'idSala': id_sala,
              'fecha': fecha}
    return HttpResponse(view_turnos.getTurnosDisponibles(**kwargs))


def get_next_day_line(request):
    fecha = request.GET['fecha']
    id_sala = request.GET['id-sala']
    id_medico = request.GET.get('id-medico') or 0
    sp = fecha.split('-')
    c = date(int(sp[0]), int(sp[1]), int(sp[2]))
    next_date = _get_next_day(c, id_sala, id_medico)
    day_lines = [_get_day_lines(next_date, id_sala)]
    view_turnos = ViewTurnos()
    return HttpResponse(view_turnos.getDayLines(day_lines))


def get_back_day_line(request):
    fecha = request.GET['fecha']
    id_sala = request.GET['id-sala']
    id_medico = request.GET.get('id-medico') or 0
    sp = fecha.split('-')
    c = date(int(sp[0]), int(sp[1]), int(sp[2]))
    back_date = _get_previous_day(c, id_sala, id_medico)
    day_lines = [_get_day_lines(back_date, id_sala)]
    view_turnos = ViewTurnos()
    return HttpResponse(view_turnos.getDayLines(day_lines))


def guardar(request):
    err_ses = 'Error, la sesión se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo.'
    err_sup = 'Error, se ha detectado superposición de turnos. Por favor, haga click en Mostrar y vuelva a intentarlo.'
    # session check
    if request.session.get('cedir_user_id') is None:
        resp_dict = {'status': 0, 'message': err_ses}
        json = simplejson.dumps(resp_dict)
        return HttpResponse(json)

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
        resp_dict = {'status': 0, 'message': err_sup}
        json = simplejson.dumps(resp_dict)
        return HttpResponse(json)

    id_paciente = request.GET['id-paciente']
    id_practicas = request.GET.getlist('id-practicas[]')
    id_medico = request.GET['id-medico']
    id_obra_social = request.GET['id-obra-social']
    observacion_turno = request.GET['observacion_turno']

    paciente = Paciente.objects.get(id=id_paciente)
    practicas = Practica.objects.filter(id__in=id_practicas)

    try:
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

        log = AuditLog()
        log.user = Usuario.objects.get(id=int(request.session.get('cedir_user_id')))
        log.userActionId = 1
        log.objectTypeId = 3
        log.objectId = turno.id
        log.dateTime = datetime.now()
        log.observacion = ''
        log.save()

        resp_dict = {'status': 1, 'message': "El turno se ha creado correctamente."}
        json = simplejson.dumps(resp_dict)
        return HttpResponse(json)

    except Exception as err:
        return str(err)


def update(request, id_turno):
    id_obra_social = request.GET['id-obra-social']
    observacion = request.GET['observacion']

    turno = Turno.objects.get(id=id_turno)

    if turno is None:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    obra_social = ObraSocial.objects.get(id=id_obra_social)

    try:
        # turno.estado_id = idEstado
        turno.obraSocial = obra_social
        turno.observacion = observacion
        turno.save()

        response_dict = {'status': 1, 'message': "El turno se ha guardado correctamente."}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    except Exception as err:
        return str(err)


def anunciar(request, id_turno):
    try:
        turno = Turno.objects.get(id=id_turno)
    except Turno.DoesNotExist:
        response_dict = {'status': False, 'message': "Error, no existe turno"}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    try:
        practicas = turno.practicas.all()
        for practica in practicas:
            estudio = Estudio()
            estudio.paciente_id = turno.paciente.id
            estudio.practica_id = practica.id
            estudio.fechaEstudio = turno.fechaTurno
            estudio.motivoEstudio = ""
            estudio.informe = ""
            estudio.medico_id = turno.medico.id
            estudio.obraSocial_id = turno.obraSocial.id
            estudio.medicoSolicitante_id = turno.medico.id
            estudio.idFacturacion = 0
            estudio.nroDeOrden = ""
            estudio.anestesista_id = 1
            estudio.esPagoContraFactura = 0
            estudio.fechaCobro = None
            estudio.importeEstudio = 0
            estudio.importeMedicacion = 0
            estudio.pagoContraFactura = 0
            estudio.diferenciaPaciente = 0
            estudio.pension = 0
            estudio.importe_pago_medico = 0
            estudio.importe_pago_medico_solicitante = 0
            estudio.pago_medico_actuante = None
            estudio.pago_medico_solicitante = None
            estudio.importeCobradoPension = 0
            estudio.importeCobradoArancelAnestesia = 0
            estudio.importeEstudioCobrado = 0
            estudio.importeMedicacionCobrado = 0
            estudio.arancelAnestesia = 0
            estudio.save()
            estudio.public_id = encode(estudio.id)
            estudio.save()

            # log estudio
            log = AuditLog()
            log.user = Usuario.objects.get(id=int(request.session.get('cedir_user_id')))
            log.userActionId = 1
            log.objectTypeId = 1
            log.objectId = estudio.id
            log.dateTime = datetime.now()
            log.observacion = 'creado desde turnos'
            log.save()

        response_dict = {'status': True, 'message': "Success"}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    except Exception as err:
        response_dict = {'status': False, 'message': str(err)}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)


def anular(request, id_turno):
    turno = Turno.objects.get(id=id_turno)
    if turno is None:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    estado = Estado.objects.get(id=3)
    try:
        turno.estado = estado
        turno.save()
        response_dict = {'status': 1, 'message': "El turno se ha anulado correctamente."}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)
    except Exception as err:
        return str(err)


def reprogramar(request, id_turno):
    turno = Turno.objects.get(id=id_turno)
    if turno is None:
        return get_buscar_turnos(request)

    estado = Estado.objects.get(id=3)
    try:
        turno.estado = estado
        turno.save()
        practicas = turno.practicas.all()
        kwargs = {
            'id-sala': turno.sala.id,
            'id-paciente': turno.paciente.id,
            'id-medico': turno.medico.id,
            'id-obra-social': turno.obraSocial.id,
            'id-practicas[]': [str(practica.id) for practica in practicas]
        }
        return get_turnos_disponibles(request, **kwargs)
    except Exception as err:
        return str(err)


def confirmar(request, id_turno):
    turno = Turno.objects.get(id=id_turno)
    if turno is None:
        response_dict = {'status': 0, 'message': "Error, no existe turno"}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    estado = Estado.objects.get(id=2)
    try:
        turno.estado = estado
        turno.save()
        response_dict = {'status': 1, 'message': "El turno se ha confirmado correctamente."}
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)
    except Exception as err:
        return str(err)


def _get_day_lines(fecha, id_sala):
    dia = spaDays[fecha.weekday()]
    mes = spaMonths[fecha.month]
    return {
        "fecha": str(fecha),
        "dia": dia + ' ' + str(fecha.day) + ' de ' + mes + ' del ' + str(fecha.year),
        "turnos": Turno.objects.filter(fechaTurno=fecha, sala__id=int(id_sala), estado__id__lt=3),
        "disponibilidad": _get_disponibilidad(dia, id_sala)
    }


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


def _get_disponibilidad(dia, id_sala):
    today = date.today()
    disponibilidades = Disponibilidad.objects \
        .filter(dia=dia, sala__id=id_sala, fecha__lte=today) \
        .order_by('horaInicio')

    # como se trae el historial de disp menor a hoy, hay que tomar la de fecha mas alta por medico*.
    # Esa logica puede hacerse aca
    # *se asume que en un dia determinado (lunes) el medico solo atiende una vez en esa sala
    return disponibilidades


class InfoTurnoViewSet(viewsets.ModelViewSet):
    model = InfoTurno
    queryset = InfoTurno.objects.all()
    serializer_class = InfoTurnoSerializer

    def get_queryset(self):
        queryset = InfoTurno.objects.all()
        medico_id = self.request.query_params.get(u'medico')
        practica_ids = self.request.query_params.get(u'practicas')
        obra_social_ids = self.request.query_params.get(u'obras_sociales')

        if medico_id:
            queryset = queryset.filter(Q(medico=medico_id) | Q(medico__isnull=True))

        if obra_social_ids:
            queryset = queryset.filter(
                Q(obra_sociales__id__in=obra_social_ids.split(u','))
                |
                Q(obra_sociales__isnull=True)
            )

        if practica_ids:
            queryset = queryset.filter(Q(practicas__id__in=practica_ids.split(u',')) | Q(practicas__isnull=True))

        return queryset.distinct()
