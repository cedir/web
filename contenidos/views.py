import logging
import smtplib
from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.template.loader import select_template
#from django.shortcuts import render
from contenidos.models import Contenido
from estudio.models import Estudio


logger = logging.getLogger(u'videos')
NOVEDADES_CATEGORY_ID = 2

def get_home(request):

    slide_contents = Contenido.objects.filter(categoria__name__contains='Home slide', publishContent=True).order_by("publishInitDate")
    novedades = Contenido.objects.filter(categoria__id__exact=NOVEDADES_CATEGORY_ID, publishContent=True).order_by("-createdDate")[:3]
    context = {
        u'novedades': novedades,
        u'slide_contents': slide_contents
    }
    t = select_template(['home/index.html'])
    return HttpResponse(t.render(RequestContext(request, context)))

def get_video(request, public_id):
    """
    Get the estudio for the given public_id, and displays the video link that redirects to the video download page.
    """    
    video_url = None
    paciente = None
    fecha_vencimiento = None
    link_vencido = True
    estudio_does_not_exist = False

    try:
        estudio = Estudio.objects.get(public_id=public_id)
        video_url = estudio.enlace_video
        paciente = str(estudio.paciente)
        fecha_vencimiento = estudio.fecha_vencimiento_link_video
        link_vencido = estudio.is_link_vencido()

        logger.info('Acceso correcto con public_id: %s' % public_id)
    except Estudio.DoesNotExist:
        estudio_does_not_exist = True
        logger.error('Intento con public_id erroneo: %s' % public_id)

    context = {
        u'video_url': video_url,
        u'paciente': paciente,
        u'fecha_vencimiento': fecha_vencimiento,
        u'link_vencido': link_vencido,
        u'estudio_does_not_exist': estudio_does_not_exist,
    }
    t = select_template(['pages/video_details.html'])
    return HttpResponse(t.render(RequestContext(request, context)))

def send_mail(request):
    toaddrs = settings.EMAIL_NOTIFICATION_ACCOUNTS
    subject = "Subject: Nuevo mensaje registrado desde cedirsalud.com.ar\n\n"

    gmail_user = settings.EMAIL_ACCOUNT_USER
    gmail_pwd = settings.EMAIL_ACCOUNT_PSW

    name = request.POST['name']
    email = request.POST['email']
    tel = request.POST['tel']
    message = request.POST['message']

    msg = subject + 'Nombre: ' + name + "\n" + 'Mail: ' + email + "\n" + 'Tel: ' + tel + "\n" + 'Mensaje: ' + message + "\n"

    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    smtpserver.sendmail(gmail_user, toaddrs, msg)
    smtpserver.close()

    templateName = 'contacto_ok.html'
    t = select_template(['pages/' + templateName])

    c = Context({
        #'latest_poll_list': latest_poll_list,
	    #'current_date': now,
    })
    return HttpResponse(t.render(RequestContext(request, c)))

