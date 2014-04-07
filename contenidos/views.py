# Create your views here.


from django.http import HttpResponse
from django.template import Template, Context, loader

from contenidos.models import *

def getContent(request, idContent):
    
    templateName = 'getContent.html'
    if (request.GET.has_key('template') and request.GET['template'] != ''):
    	templateName = request.GET['template']
    
    cContent = Contenido.objects.get(pk=1)
    
    
    c = Context({
	'content': cContent,
    })
    
    
    t = loader.get_template('pages/' + templateName)
    return HttpResponse(t.render(c))