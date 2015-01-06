from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import select_template
from django.shortcuts import render
from contenidos.models import *
from estudio.models import Estudio

def get_video(request, public_id):
    """
    
    """    
    video_url = None
    paciente = None
    fecha_vencimiento = None
    link_vencido = True

    try:
        #estudio = Estudio.object.get(public_id=public_id)
        #video_url = estudio.enlace_video
        estudio = Estudio.objects.get(pk=public_id)
        video_url = estudio.enlace_video

        paciente = str(estudio.paciente)
        fecha_vencimiento = estudio.fecha_vencimiento_link_video
        link_vencido = estudio.is_link_vencido()
    except Estudio.DoesNotExist:
        pass

    context = {
        u'video_url': video_url,
        u'paciente': paciente,
        u'fecha_vencimiento': fecha_vencimiento,
        u'link_vencido': link_vencido,
    }
    t = select_template(['pages/video_details.html'])
    return HttpResponse(t.render(RequestContext(request, context)))

