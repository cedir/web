# -*- coding: utf-8 -*-
from datetime import datetime
import simplejson

from django.conf import settings
from django.shortcuts import redirect
from django.template import Template, Context, loader
from django.http import HttpResponse
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework import viewsets, filters
from rest_framework.decorators import list_route, detail_route

from common.drf.views import StandardResultsSetPagination
from medico.models import Medico, Disponibilidad, PagoMedico
from medico.serializers import MedicoSerializer, PagoMedicoSerializer, ListNuevoPagoMedicoSerializer, CreateNuevoPagoMedicoSerializer, GETLineaPagoMedicoSerializer
from sala.models import Sala
from estudio.models import Estudio


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


class MedicoNombreApellidoOMatriculaFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_text = request.query_params.get(u'search_text')

        if search_text:
            if unicode.isdigit(search_text):
                queryset = queryset.filter(Q(matricula__icontains=search_text))
            else:
                search_params = [x.strip() for x in search_text.split(',')]
                nomOApe1 = search_params[0]
                nomOApe2 = search_params[1] if len(search_params) >= 2 else ''
                queryset = queryset.filter((Q(nombre__icontains=nomOApe1) & Q(apellido__icontains=nomOApe2)) |
                                           (Q(nombre__icontains=nomOApe2) & Q(apellido__icontains=nomOApe1)))
        return queryset


class MedicoViewSet(viewsets.ModelViewSet):
    model = Medico
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    filter_backends = (MedicoNombreApellidoOMatriculaFilterBackend, )
    pagination_class = None

    @detail_route(methods=['get'])
    def get_estudios_pendientes_de_pago(self, request, pk=None):
        # Si la fecha de cobro es null, no se lo cobramos a la OS
        # Si es pago_contra_factura entonces hay que cobrarle al medico los servicios administrativos
        estudios_cobrados = Estudio.objects.filter(fecha_cobro__isnull=False) \
                            | Estudio.objects.filter(pago_contra_factura=True)
        # Si el medico participo en el estudio (como actuante o solicitante)
        # y no se lo pagamos/cobramos, esta pendiente.
        pendientes_del_medico = estudios_cobrados.filter(medico__id=pk, pago_medico_actuante__isnull=True) \
                                | estudios_cobrados.filter(medico_solicitante__id=pk, pago_medico_solicitante__isnull=True)
        data = [ListNuevoPagoMedicoSerializer(q, context={'calculador': 1}).data for q in pendientes_del_medico]
        return Response(data)


class PagoMedicoViewList(viewsets.ModelViewSet):  # TODO: solo allow list, get y POST
    queryset = PagoMedico.objects.all().order_by('-fecha')
    serializer_class = PagoMedicoSerializer
    pagination_class = StandardResultsSetPagination
    page_size = 20

    def create(self, request, *args, **kwargs):
        serializer = CreateNuevoPagoMedicoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #serializer.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def get_detalle_pago(self, request, pk=None):

        pago_medico = PagoMedico.objects.get(pk=pk)

        # TODO: merge these
        # TODO: mostrar solo el total para medico actuante o solicitante de acuerdo al rol en el estudio
        # en vez de mostrar los importes actuante y solicitante todo el tiempo
        # TODO: ver donde devolver el total
        estudios_actuante = pago_medico.estudios_actuantes.all()
        estudios_solicitantes = pago_medico.estudios_solicitantes.all()
        data = []
        serializer = GETLineaPagoMedicoSerializer(estudios_actuante, many=True)
        data.append(serializer.data)

        return Response(data)
