import logging
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import select_template
from django.shortcuts import render
from contenidos.models import *
from estudio.models import Estudio


logger = logging.getLogger(u'videos')

def get_video(request, public_id):
    """
    Get the estudio for the given public_id, and displays the video link that redirects to the video download page.
    """    
    video_url = None
    paciente = None
    fecha_vencimiento = None
    link_vencido = True

    try:
        estudio = Estudio.objects.get(public_id=public_id)
        video_url = estudio.enlace_video
        paciente = str(estudio.paciente)
        fecha_vencimiento = estudio.fecha_vencimiento_link_video
        link_vencido = estudio.is_link_vencido()

        logger.info('Acceso correcto con public_id: %s' % public_id)
    except Estudio.DoesNotExist:
        logger.error('Intento con public_id erroneo: %s' % public_id)
        pass

    context = {
        u'video_url': video_url,
        u'paciente': paciente,
        u'fecha_vencimiento': fecha_vencimiento,
        u'link_vencido': link_vencido,
    }
    t = select_template(['pages/video_details.html'])
    return HttpResponse(t.render(RequestContext(request, context)))

