from django.http import HttpResponse
from django.template import loader

def getStatic(request, templateName = 'default.html'):

    flash_buttonId = ''
    if ('buttonId' in request.GET and request.GET['buttonId'] != ''):
        flash_buttonId = request.GET['buttonId']

    if ('name' in request.GET and request.GET['name'] != ''):
        templateName = request.GET['name']

    t = loader.get_template('pages/' + templateName)


    c = {
    'flash_button_id': flash_buttonId,
    }
    return HttpResponse(t.render(c))