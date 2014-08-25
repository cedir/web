# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Template, Context, loader
from datetime import datetime
from managers.view.root import *
from managers.model.personas import *
from managers.model.turno import *
import simplejson

class Root():

  def __init__(self, request):
    self.request = request

  def getLogin(self):
    viewRoot = ViewRoot(self.request)
    return viewRoot.getLogin()

  def login(self):
    request = self.request
    usuario = request.POST['txtNomUsuario']
    password = request.POST['txtPassword']

    try:
      obj_user = Usuario.objects.get(nombreUsuario=usuario)
      if obj_user.password == password:
	request.session['cedir_user_id'] = obj_user.id
	request.session['cedir_user_name'] = obj_user.nombreUsuario
	request.session.set_expiry(0)
	return self.getHome()
      else:
	return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=1&next=%s' % request.path)
    except:
      return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=1&next=%s' % request.path)

  def logout(self):
    request = self.request
    try:
	del request.session['cedir_user_id']
    except KeyError:
	pass
    return self.getLogin()

  def getHome(self):
    request = self.request
    #session check
    if request.session.get('cedir_user_id') is None:
      return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

    viewRoot = ViewRoot(self.request)
    return viewRoot.getHome()

  def getDisponibilidadMedicos(self):
    request = self.request
    #session check
    if request.session.get('cedir_user_id') is None:
      return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

    cond = {}

    idMedico = 0
    if request.GET.has_key('id-medico') and request.GET['id-medico'] != "":
      idMedico = request.GET['id-medico']
      cond["medico__id"] = idMedico

    medicos = Medico.objects.all().order_by("apellido")
    disponibilidades = Disponibilidad.objects.filter(**cond).order_by('medico__apellido')
    salas = Sala.objects.all().order_by('id')
    dias = [{'id':'lunes','nombre':'Lunes'},{'id':'martes','nombre':'Martes'},{'id':'miercoles','nombre':'Miercoles'},{'id':'jueves','nombre':'Jueves'},{'id':'viernes','nombre':'Viernes'},{'id':'sabado','nombre':'Sabado'}]

    viewRoot = ViewRoot(self.request)
    kwargs = {'idMedico':idMedico,'medicos':medicos,'disponibilidades':disponibilidades,'salas':salas,'dias':dias}
    return viewRoot.getDisponibilidadMedicos(**kwargs)

  def getDisponibilidadMedicosJson(self):
    request = self.request
    #session check
    if request.session.get('cedir_user_id') is None:
      response_dict['status'] = 0
      response_dict['message'] = "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
      json = simplejson.dumps(response_dict)
      return json

    cond = {}

    idMedico = 0
    if request.GET.has_key('id-medico') and request.GET['id-medico'] != "":
      idMedico = request.GET['id-medico']
      cond["medico__id"] = idMedico

    disponibilidades = Disponibilidad.objects.filter(**cond)    

    viewRoot = ViewRoot(self.request)
    kwargs = {'idMedico':idMedico,'disponibilidades':disponibilidades}
    return viewRoot.getDisponibilidadMedicosJson(**kwargs)

  def crearDisponibilidad(self):
    request = self.request
    response_dict = {}
    #session check
    if request.session.get('cedir_user_id') is None:
      response_dict['status'] = 0
      response_dict['message'] = "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
      json = simplejson.dumps(response_dict)
      return json

    disponibilidad = Disponibilidad()
    disponibilidad.dia = request.POST['id-dia']
    disponibilidad.horaInicio = request.POST['hora_desde']
    disponibilidad.horaFin = request.POST['hora_hasta']
    disponibilidad.fecha = datetime.now()
    disponibilidad.medico_id = request.POST['id-medico']
    disponibilidad.sala_id = request.POST['id-sala']
    disponibilidad.save(force_insert=True)

    response_dict['status'] = 1
    response_dict['message'] = "El horario se ha creado correctamente."
    json = simplejson.dumps(response_dict)
    return json

  def getDisponibilidad(self):
    request = self.request
    response_dict = {}
    #session check
    if request.session.get('cedir_user_id') is None:
      response_dict['status'] = 0
      response_dict['message'] = "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
      json = simplejson.dumps(response_dict)
      return json

    idDisponibilidad = request.GET['id']
    disponibilidad = Disponibilidad.objects.get(id=idDisponibilidad)
    viewRoot = ViewRoot()
    kwargs = {'disponibilidad':disponibilidad}
    return viewRoot.getDisponibilidad(**kwargs)

  def updateDisponibilidad(self):
    request = self.request
    response_dict = {}
    #session check
    if request.session.get('cedir_user_id') is None:
      response_dict['status'] = 0
      response_dict['message'] = "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
      json = simplejson.dumps(response_dict)
      return json

    idDisponibilidad = request.POST['id']
    disponibilidad = Disponibilidad.objects.get(id=idDisponibilidad)
    disponibilidad.dia = request.POST['id-dia']
    disponibilidad.horaInicio = request.POST['hora_desde']
    disponibilidad.horaFin = request.POST['hora_hasta']
    disponibilidad.fecha = datetime.now()
    disponibilidad.medico_id = request.POST['id-medico']
    disponibilidad.sala_id = request.POST['id-sala']
    disponibilidad.save()

    response_dict['status'] = 1
    response_dict['message'] = "El horario se ha actualizado correctamente."
    json = simplejson.dumps(response_dict)
    return json
    
  def deleteDisponibilidad(self):
    request = self.request
    response_dict = {}
    #session check
    if request.session.get('cedir_user_id') is None:
      response_dict['status'] = 0
      response_dict['message'] = "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
      json = simplejson.dumps(response_dict)
      return json

    idDisponibilidad = request.POST['id']
    disponibilidad = Disponibilidad.objects.get(id=idDisponibilidad)
    disponibilidad.delete()

    response_dict['status'] = 1
    response_dict['message'] = "El horario ha sido eleiminado correctamente."
    json = simplejson.dumps(response_dict)
    return json