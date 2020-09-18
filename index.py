from django.http import HttpResponse
import datetime
from django.template import Template, loader

from .contenidos.models import *
import os


def render_home(request):

    t = loader.get_template('includes/tipo1.html')
    contents = Contenido.objects.filter(categoria__id__exact=1, publishContent=True).order_by("createdDate")
    destacados_contents = Contenido.objects.filter(publishContent=True, destacarContent=True)

    arrDestacados_contents = []
    for cContent in destacados_contents:
        filePathName, ext = os.path.splitext(cContent.img1.name)
        contents_dicc = {}
        contents_dicc["id"] = cContent.id
        contents_dicc["title"] =cContent.title
        contents_dicc["description"] = cContent.description
        contents_dicc["footer"] = cContent.footer
        contents_dicc["img1_min"] = filePathName + '_min' + ext
        contents_dicc["friendlyURL"] = cContent.friendlyURL

        arrDestacados_contents.append(contents_dicc)

    c = {
        'home_contents': contents,
        'destacados_contents': arrDestacados_contents,
        'flash_button_id': 1,
    }
    return HttpResponse(t.render(c))

