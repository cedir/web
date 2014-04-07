# Create your views here.


from django.http import HttpResponse
from django.template import Template, Context, loader

from contenidos.models import *
import os

def getList(request):
    
    flash_buttonId = ''
    if (request.GET.has_key('buttonId') and request.GET['buttonId'] != ''):
	flash_buttonId = request.GET['buttonId']

    categoryId = 1
    if (request.GET.has_key('categoryId') and request.GET['categoryId'] != ''):
	categoryId = request.GET['categoryId']


    #Parche para ordenar novedades for fecha, hacerlo bien
    order_by = 'title'
    if (request.GET.has_key('template') and request.GET['template'] == 'novedades.html'):
      order_by = 'createdDate'


    contents = Contenido.objects.filter(categoria__id__exact=categoryId, publishContent='TRUE').order_by(order_by)
    
    arrContents = []
    for cContent in contents:
	filePathName, ext = os.path.splitext(cContent.img1.name)
	contents_dicc = {}
	contents_dicc["id"] = cContent.id
	contents_dicc["title"] =cContent.title
	contents_dicc["description"] = cContent.description
	contents_dicc["footer"] = cContent.footer
	contents_dicc["friendlyURL"] = cContent.friendlyURL
	contents_dicc["img1"] = cContent.img1
	if cContent.img1:
	    contents_dicc["img1_min"] = filePathName + '_min' + ext
	
	arrContents.append(contents_dicc)
    
    c = Context({
	'contents': arrContents,
	'flash_button_id': flash_buttonId,
    })
    
    templateName = 'getContentsList.html'
    if (request.GET.has_key('template') and request.GET['template'] != ''):
	templateName = request.GET['template']
    t = loader.get_template('pages/' + templateName)
	
    return HttpResponse(t.render(c))