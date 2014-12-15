from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import select_template
from django.shortcuts import render
from contenidos.models import *
from estudio.models import Estudio

def get_video(request, public_id):

        video_url = None

        try:
            estudio = Estudio.object.get(public_id=public_id)
            video_url = estudio.video
        except Estudio.DoesNotExist:
            pass

        context = {
            'video_url' : video_url
        }
        t = select_template(['pages/video_details.html'])
        return HttpResponse(t.render(RequestContext(request, context)))

