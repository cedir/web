from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Template, Context, loader
from datetime import datetime
from managers.view.pacientes import *
from managers.model.personas import *
import simplejson
from decimal import *


class Pacientes():

  def __init__(self, request):
    self.request = request

  def getCreate(self):
    request = self.request
    #session check
    if request.session.get('cedir_user_id') is None:
      return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

    viewPacientes = ViewPacientes(request)
    return viewPacientes.getCreate()
  
  def getUpdate(self):
    request = self.request
    #session check
    if request.session.get('cedir_user_id') is None:
      return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)


    idPaciente = request.GET['id']

    paciente = Paciente.objects.get(pk=idPaciente)
    viewPacientes = ViewPacientes(request)
    return viewPacientes.getUpdate(paciente)

  def getBuscar(self):
    request = self.request
    
    #session check
    if request.session.get('cedir_user_id') is None:
      return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

    cond = {}

    apellido = ""
    if request.GET.has_key('apellido') and request.GET['apellido'] != "":
      apellido = request.GET['apellido']
      cond["apellido__icontains"] = apellido
      
    nombre = ""
    if request.GET.has_key('nombre') and request.GET['nombre'] != "":
      nombre = request.GET['nombre']
      cond["nombre__icontains"] = nombre

    dni = ""
    if request.GET.has_key('dni') and request.GET['dni'] != "":
      dni = request.GET['dni']
      cond["dni"] = dni

    requestType = ""
    if request.GET.has_key('requestType') and request.GET['requestType'] != "":
      requestType = request.GET['requestType']

    arrPacientes = Paciente.objects.filter(**cond).order_by("apellido", "nombre")[:75]

    viewPacientes = ViewPacientes(request)
    kwViewArgs = {'pacientes':arrPacientes, 'dni':dni, 'apellido':apellido, 'requestType':requestType }
    return viewPacientes.getBuscar(**kwViewArgs)


  def crear(self):
    request = self.request
    domicilio = ""
    if request.POST.has_key('domicilio') and request.POST['domicilio'] != "":domicilio = request.POST['domicilio']
    sexo = ""
    if request.POST.has_key('sexo') and request.POST['sexo'] != "":sexo = request.POST['sexo']
    fechaNacimiento = None
    if request.POST.has_key('fechaNacimiento') and request.POST['fechaNacimiento'] != "":fechaNacimiento = datetime.strptime(request.POST['fechaNacimiento'], '%d/%m/%Y')
    dni = 0
    if request.POST.has_key('dni') and request.POST['dni'] != "":dni = int(request.POST['dni'])

    response_dict = {}

    if dni > 0: #revisar que el DNI no este duplicado, a menos que sea 0
      pacientes = Paciente.objects.filter(dni=dni)
      if len(pacientes) > 0:
	response_dict['status'] = 0
	response_dict['message'] = "Error, ya existe un paciente con DNI " + str(dni)
	json = simplejson.dumps(response_dict)
	return json

    try :
      paciente = Paciente()
      paciente.nombre = request.POST['nombre']
      paciente.apellido = request.POST['apellido']
      paciente.dni = dni
      paciente.domicilio = domicilio
      paciente.telefono = request.POST['telefono']
      paciente.sexo = sexo
      paciente.fechaNacimiento = fechaNacimiento
      paciente.save(force_insert=True)

      response_dict['idPaciente'] = paciente.id
      response_dict['status'] = 1
      response_dict['message'] = "El paciente se ha creado correctamente."
      json = simplejson.dumps(response_dict)
      return json
    except Exception, err:
      response_dict['status'] = 0
      response_dict['message'] = "Ocurrio un error. Revise los datos y vuelva a intentarlo."
      json = simplejson.dumps(response_dict)
      return json

  def update(self):
    request = self.request
    domicilio = ""
    if request.POST.has_key('domicilio') and request.POST['domicilio'] != "":domicilio = request.POST['domicilio']
    sexo = ""
    if request.POST.has_key('sexo') and request.POST['sexo'] != "":sexo = request.POST['sexo']
    fechaNacimiento = None
    if request.POST.has_key('fechaNacimiento') and request.POST['fechaNacimiento'] != "":fechaNacimiento = datetime.strptime(request.POST['fechaNacimiento'], '%d/%m/%Y')
    dni = 0
    if request.POST.has_key('dni') and request.POST['dni'] != "":dni = request.POST['dni']

    response_dict = {}
    
    paciente = Paciente.objects.get(id=request.POST['id'])
    
    if dni > 0: #revisar que el DNI no este duplicado, a menos que sea 0
      pacientes = Paciente.objects.filter(dni=dni)
      if len(pacientes) > 0 and pacientes[0].id <> paciente.id:
	response_dict['status'] = 0
	response_dict['message'] = "Error, ya existe un paciente con DNI " + str(dni)
	json = simplejson.dumps(response_dict)
	return json

    try :
      paciente.dni = dni
      paciente.nombre = request.POST['nombre']
      paciente.apellido = request.POST['apellido']
      paciente.domicilio = domicilio
      paciente.telefono = request.POST['telefono']
      paciente.sexo = sexo
      paciente.fechaNacimiento = fechaNacimiento
      paciente.save()

      response_dict['status'] = 1
      response_dict['message'] = "El paciente se ha modificado correctamente."
      json = simplejson.dumps(response_dict)
      return json
    except Exception, err:
      response_dict['status'] = 0
      response_dict['message'] = "Ocurrio un error. Revise los datos y vuelva a intentarlo." + "Error:" + str(err)
      json = simplejson.dumps(response_dict)
      return json
