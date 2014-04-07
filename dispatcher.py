from django.http import HttpResponse

from managers.controller.turnos import *
from managers.controller.root import *
from managers.controller.pacientes import *

def dispatch(request):
    if (request.GET.has_key('controlador')):
      controlador_string = request.GET['controlador']
    else:
      controlador_string = request.POST['controlador']

    if (request.GET.has_key('accion')):
      accion_string = request.GET['accion']
    else:
      accion_string = request.POST['accion']

    controlador = eval(controlador_string)(request)
    method = getattr(controlador, accion_string)

    obj_response = method()

    if type(obj_response).__name__ == 'HttpResponseRedirect':
      return method()
    else:
      return HttpResponse(obj_response)



def getLogin(request):
    root = Root(request)
    return HttpResponse(root.getLogin())