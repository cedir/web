# -*- coding: utf-8 -*-
from django.http import HttpResponse
from rest_framework import viewsets, filters
from django.db.models import Q
from medico.models import Medico, Disponibilidad
from medico.serializers import MedicoSerializer
from sala.models import Sala
from django.conf import settings
from django.shortcuts import redirect
from django.template import Template, Context, loader
from datetime import datetime
import simplejson


def get_disponibilidad_medicos(request):
    # session check
    if not request.user.is_authenticated():
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    cond = {}

    id_medico = request.GET.get('id-medico', 0)
    if id_medico:
        cond["medico__id"] = id_medico

    medicos = Medico.objects.all().order_by("apellido")
    disponibilidades = Disponibilidad.objects.filter(**cond).order_by('medico__apellido')
    salas = Sala.objects.all().order_by('id')
    dias = [{'id': 'lunes', 'nombre': 'Lunes'}, {'id': 'martes', 'nombre': 'Martes'},
            {'id': 'miercoles', 'nombre': 'Miercoles'}, {'id': 'jueves', 'nombre': 'Jueves'},
            {'id': 'viernes', 'nombre': 'Viernes'}, {'id': 'sabado', 'nombre': 'Sabado'}]

    arr_medicos = [{
        "id":  medico.id,
        "nombre": medico.nombre,
        "apellido": medico.apellido,
        "selected": 1 if medico.id == int(id_medico) else 0
    } for medico in medicos]

    arr_disponibilidades = [{
        "id": disp.id, "dia": disp.dia,
        "horaInicio": disp.horaInicio, "horaFin": disp.horaFin,
        "medico": disp.medico.apellido + ", " + disp.medico.nombre,
        "sala": disp.sala.nombre
    } for disp in disponibilidades]

    arr_salas = [{
        "id": sala.id, "nombre": sala.nombre
    } for sala in salas]

    c = Context({
      'logged_user_name': request.user.username,
      'medicos': arr_medicos,
      'disponibilidades':arr_disponibilidades,
      'salas': arr_salas,
      'dias': dias,
    })

    t = loader.get_template('turnos/disponibilidadMedicosAMB.html')

    return HttpResponse(t.render(c))


def get_disponibilidad_medico(request, id_medico):
    # session check
    if not request.user.is_authenticated():
        response_dict = {
            'status': 0,
            'message': "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
        }
        return simplejson.dumps(response_dict)

    cond = {}

    if id_medico:
        cond["medico__id"] = id_medico

    disponibilidades = Disponibilidad.objects.filter(**cond)
    response_dict = {'horario': ""}

    for disp in disponibilidades:
        response_dict['horario'] += "<br />" + disp.dia + " de " + str(disp.horaInicio) + "hs a " + str(
            disp.horaFin) + "hs - " + disp.sala.nombre

    return HttpResponse(simplejson.dumps(response_dict))


def get_disponibilidad(request, id_disponibilidad):
    # session check
    if not request.user.is_authenticated():
        response_dict = {
            'status': 0,
            'message': "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
        }
        return simplejson.dumps(response_dict)

    disponibilidad = Disponibilidad.objects.get(id=id_disponibilidad)

    response_dict = {
        'id': disponibilidad.id, "hora_inicio": str(disponibilidad.horaInicio),
        "hora_fin": str(disponibilidad.horaFin), "medico": disponibilidad.medico.id,
        "dia": disponibilidad.dia, "sala": disponibilidad.sala.id
    }

    return HttpResponse(simplejson.dumps(response_dict))


def create_disponibilidad(request):
    # session check
    if not request.user.is_authenticated():
        response_dict = {
            'status': 0,
            'message': "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
        }
        return simplejson.dumps(response_dict)

    disponibilidad = Disponibilidad()
    disponibilidad.dia = request.POST['id-dia']
    disponibilidad.horaInicio = request.POST['hora_desde']
    disponibilidad.horaFin = request.POST['hora_hasta']
    disponibilidad.fecha = datetime.now()
    disponibilidad.medico_id = request.POST['id-medico']
    disponibilidad.sala_id = request.POST['id-sala']
    disponibilidad.save(force_insert=True)

    response_dict = {
        'status': 1,
        'message': "El horario se ha creado correctamente."
    }

    return HttpResponse(simplejson.dumps(response_dict))


def update_disponibilidad(request, id_disponibilidad):
    # session check
    if not request.user.is_authenticated():
        response_dict = {
            'status': 0,
            'message': "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
        }
        return simplejson.dumps(response_dict)

    disponibilidad = Disponibilidad.objects.get(id=id_disponibilidad)
    disponibilidad.dia = request.POST['id-dia']
    disponibilidad.horaInicio = request.POST['hora_desde']
    disponibilidad.horaFin = request.POST['hora_hasta']
    disponibilidad.fecha = datetime.now()
    disponibilidad.medico_id = request.POST['id-medico']
    disponibilidad.sala_id = request.POST['id-sala']
    disponibilidad.save()

    response_dict = {
        'status': 1,
        'message': "El horario se ha actualizado correctamente."
    }
    return HttpResponse(simplejson.dumps(response_dict))


def delete_disponibilidad(request, id_disponibilidad):
    # session check
    if not request.user.is_authenticated():
        response_dict = {
            'status': 0,
            'message': "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
        }
        return simplejson.dumps(response_dict)

    disponibilidad = Disponibilidad.objects.get(id=id_disponibilidad)
    disponibilidad.delete()

    response_dict = {
        'status': 1,
        'message': "El horario ha sido eliminado correctamente."
    }
    return HttpResponse(simplejson.dumps(response_dict))

class MedicoNombreApellidoFilterBackend(filters.BaseFilterBackend):

    """
    Filtro de medicos por nombre o apellido
    """
    def filter_queryset(self, request, queryset, view):
        search_text = request.query_params.get(u'search_text')
        if search_text:
            queryset = queryset.filter(Q(nombre__icontains=search_text) | Q(apellido__icontains=search_text))
            return queryset

class MedicoViewSet(viewsets.ModelViewSet):
    model = Medico
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_backends = (MedicoNombreApellidoFilterBackend, )
    pagination_class = None
