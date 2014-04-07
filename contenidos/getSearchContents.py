# Create your views here.


from django.http import HttpResponse
from django.template import Template, Context, loader
from django.db.models import Q

from contenidos.models import *
import os

def getResults(request):
    
    categoryId = ''
    if (request.GET.has_key('categoryId') and request.GET['categoryId'] != ''):
	categoryId = request.GET['categoryId']
	
	
	
    keyWord = request.GET['keyWord']
	
    #contents = Contenido.objects.filter(Q(publishContent='TRUE'), Q(title__icontains=keyWord) | Q(description__icontains=keyWord)).order_by("title")
    
    x = Q(publishContent='TRUE')
    if categoryId != '':
    	x = x & Q(categoria__id__exact=categoryId)
	
    q = Q(title__icontains=keyWord) | Q(description__icontains=keyWord)
    condition = x & q
    
    contents = Contenido.objects.filter(condition).order_by("title")
    
    
    #si no se encontro nada, depurar keyWord y volver a buscar
    if not contents:
	words = keyWord.split(' ')
	
	arrWords = []
	if len(words) > 1:
	    for word in words:
		if len(word) > 2:
		    arrWords.append(word)
    
    	    if len(arrWords) > 0:
		q2 = None
		for word in arrWords:
		    if q2:
			q2 = q2 | Q(title__icontains=word) | Q(description__icontains=word)
		    else:
			q2 = Q(title__icontains=word) | Q(description__icontains=word)
			
		condition = x & q2
    		contents = Contenido.objects.filter(condition).order_by("title")
			
	#elif len(words) == 1:
		#habia una sola palabra, buscar en el campo desarrollo
		
    arrContents = []
    for cContent in contents:
	filePathName, ext = os.path.splitext(cContent.img1.name)
	contents_dicc = {}
	contents_dicc["id"] = cContent.id
	contents_dicc["title"] =cContent.title
	contents_dicc["description"] = cContent.description
	contents_dicc["footer"] = cContent.footer
	contents_dicc["img1"] = cContent.img1
	if cContent.img1:
	    contents_dicc["img1_min"] = filePathName + '_min' + ext
	
	arrContents.append(contents_dicc)
    
    c = Context({
	'contents': arrContents,
	'contents_counted':len(arrContents),
	'words':keyWord,
	'category_id':categoryId,
	
    })
    
    templateName = 'search_results.html'
    t = loader.get_template('pages/' + templateName)
	
    return HttpResponse(t.render(c))