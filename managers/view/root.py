# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.template import Template, Context, loader
from datetime import datetime
import simplejson

class ViewRoot():
  def __init__(self, request=None):
    self.request = request

  def getLogin(self):
    request = self.request
    errorId = request.GET.get('error_id') or 0
    
    errorMessage = ""
    if int(errorId) == 1:
      errorMessage = "Usuario o Password incorrecto."
    elif int(errorId) == 2:
      errorMessage = "Debe loguearse para ingresar al sistema de turnos."

    c = Context({
      'hora':datetime.now(),
      'error_message':errorMessage,
    })
    t = loader.get_template('turnos/login.html')
    return t.render(c)


  def getHome(self):
    request = self.request
    c = Context({
      'logged_user_name':request.session["cedir_user_name"],
    })
    t = loader.get_template('turnos/home.html')
    return t.render(c)

  def getDisponibilidadMedicos(self,**kwargs):
    request = self.request
    idMedico = kwargs['idMedico']
    medicos = kwargs['medicos']
    disponibilidades = kwargs['disponibilidades']
    salas = kwargs['salas']
    dias = kwargs['dias']

    arrMedicos = []
    for medico in medicos:
	hshMedico = {}
	hshMedico["id"] = medico.id
	hshMedico["nombre"] = medico.nombre
	hshMedico["apellido"] = medico.apellido
	if medico.id == int(idMedico):
	  hshMedico["selected"] = 1
	arrMedicos.append(hshMedico)

    arrDisponibilidades = []
    for disp in disponibilidades:
	hshRow = {}
	hshRow["id"] = disp.id
	hshRow["dia"] = disp.dia
	hshRow["horaInicio"] = disp.horaInicio
	hshRow["horaFin"] = disp.horaFin
	hshRow["medico"] = disp.medico.apellido + ", " + disp.medico.nombre
	hshRow["sala"] = disp.sala.nombre
	arrDisponibilidades.append(hshRow)

    arrSalas = []
    for sala in salas:
	hshData = {}
	hshData["id"] = sala.id
	hshData["nombre"] = sala.nombre
	arrSalas.append(hshData)


    c = Context({
      'logged_user_name':request.session["cedir_user_name"],
      'medicos':arrMedicos,
      'disponibilidades':arrDisponibilidades,
      'salas':arrSalas,
      'dias':dias,
    })
    t = loader.get_template('turnos/disponibilidadMedicosAMB.html')
    return t.render(c)
  def getDisponibilidadMedicosJson(self,**kwargs):
    request = self.request
    idMedico = kwargs['idMedico']
    disponibilidades = kwargs['disponibilidades']
    #dias = kwargs['dias']
    response_dict = {}
    response_dict['horario'] = ""

    arrDisponibilidades = []
    for disp in disponibilidades:
	response_dict['horario'] +=  "<br />" + disp.dia + " de " + str(disp.horaInicio) + "hs a " + str(disp.horaFin) + "hs - " + disp.sala.nombre

    json = simplejson.dumps(response_dict)
    return json


  def getDisponibilidad(self,**kwargs):
    disponibilidad = kwargs['disponibilidad']
    response_dict = {}
    response_dict['id'] = disponibilidad.id
    response_dict["hora_inicio"] = str(disponibilidad.horaInicio)
    response_dict["hora_fin"] = str(disponibilidad.horaFin)
    response_dict["medico"] = disponibilidad.medico.id
    response_dict["dia"] =  disponibilidad.dia
    response_dict["sala"] =  disponibilidad.sala.id

    json = simplejson.dumps(response_dict)
    return json