# Create your views here.


from django.http import HttpResponse
from django.template import loader

from contenidos.models import *

def getContent(request, idContent, templateName = 'getContent.html' ):

    flash_buttonId = ''
    if ('buttonId' in request.GET and request.GET['buttonId'] != ''):
        flash_buttonId = request.GET['buttonId']

    if ('template' in request.GET and request.GET['template'] != ''):
        templateName = request.GET['template']

    cContent = Contenido.objects.get(pk=idContent)
    filePathName1, ext1 = os.path.splitext(cContent.img1.name)
    filePathName2, ext2 = os.path.splitext(cContent.img2.name)
    filePathName3, ext3 = os.path.splitext(cContent.img3.name)

    c = {
    'id':cContent.id,
    'title':cContent.title,
    'description':cContent.description,
    'body':cContent.body,
    'footer':cContent.footer,
    'img1':cContent.img1,
    'img1_med':filePathName1 + '_med' + ext1,
    'img2':cContent.img2,
    'img2_med':filePathName2 + '_med' + ext2,
    'img3':cContent.img3,
    'img3_med':filePathName3 + '_med' + ext3,
    'flash_button_id': flash_buttonId,
    'page_title':cContent.title
    }


    t = loader.get_template('pages/' + templateName)
    return HttpResponse(t.render(c))