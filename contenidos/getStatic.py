from django.http import HttpResponse
from django.template import Template, Context, loader

def getStatic(request, templateName = 'default.html'):

    flash_buttonId = ''
    if (request.GET.has_key('buttonId') and request.GET['buttonId'] != ''):
	flash_buttonId = request.GET['buttonId']
    
    if (request.GET.has_key('name') and request.GET['name'] != ''):
    	templateName = request.GET['name']

    t = loader.get_template('pages/' + templateName)
    
    
    c = Context({
	'flash_button_id': flash_buttonId,
    })
    return HttpResponse(t.render(c))