# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.template import Template, Context, loader
from datetime import datetime

class ViewPacientes():
  def __init__(self, request=None):
    self.request = request

  def getCreate(self):
    c = Context({
      'isCreate':1,
      'logged_user_name':self.request.session["cedir_user_name"],
    })

    t = loader.get_template('turnos/ABMPaciente.html')

    return t.render(c)

  def getUpdate(self,paciente):
    fechaNacimiento = ""
    if (paciente.fechaNacimiento is not None): fechaNacimiento = paciente.fechaNacimiento.strftime("%d/%m/%Y")
    c = Context({
      'id':paciente.id,
      'dni':paciente.dni,
      'nombre':paciente.nombre,
      'apellido':paciente.apellido,
      'domicilio':paciente.domicilio,
      'telefono':paciente.telefono,
      'fechaNacimiento':fechaNacimiento,
      'sexo':paciente.sexo,
      'logged_user_name':self.request.session["cedir_user_name"],
    })

    t = loader.get_template('turnos/ABMPaciente.html')

    return t.render(c)

  def getBuscar(self, **kwargs):
    dni = kwargs['dni']
    apellido = kwargs['apellido']
    pacientes = kwargs['pacientes']
    requestType = kwargs['requestType'] or ""

    arrHshPacientes = []
    for paciente in pacientes:
	hshPeciente = {}
	hshPeciente["id"] = paciente.id
	hshPeciente["dni"] = paciente.dni
	hshPeciente["nombre"] = paciente.nombre
	hshPeciente["apellido"] = paciente.apellido
	hshPeciente["domicilio"] = paciente.domicilio or ""
	hshPeciente["telefono"] = paciente.telefono
	arrHshPacientes.append(hshPeciente)

    c = Context({
      'logged_user_name':self.request.session["cedir_user_name"],
      'pacientes': arrHshPacientes,
      'apellido': apellido,
      'dni': dni,
    })

    templateName = 'turnos/buscarPaciente.html'
    if requestType == 'ajax':
      templateName = 'turnos/buscarPacienteAjax.html'

    t = loader.get_template(templateName)

    return t.render(c)
