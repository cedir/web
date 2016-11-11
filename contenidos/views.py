import os
import logging
import smtplib
from django.http import HttpResponse, Http404
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

def get_content_friendly_url(request, friendly_url):
    """
    Soporte para frinedly URL: content/<friendly-url>
    """
    cContent = Contenido.objects.filter(friendlyURL=friendly_url).first()
    if bool(cContent):
        return get_content(request, cContent.id)
    else:
        raise Http404("No existe contenido: " + friendly_url)


def get_content(request, id_content, templateName='detalle-contenido.html' ):

    if (request.GET.has_key('template') and request.GET['template'] != ''):
        templateName = request.GET['template']

    cContent = Contenido.objects.get(pk=id_content)
    filePathName1, ext1 = os.path.splitext(cContent.img1.name)
    filePathName2, ext2 = os.path.splitext(cContent.img2.name)
    filePathName3, ext3 = os.path.splitext(cContent.img3.name)

    c = Context({
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
        'page_title':cContent.title
    })

    t = select_template(['home/{}'.format(templateName)])
    return HttpResponse(t.render(RequestContext(request, c)))

def get_list_content(request):
    categoryId = 1
    if (request.GET.has_key('categoryId') and request.GET['categoryId'] != ''):
	    categoryId = request.GET['categoryId']

    #Parche para ordenar novedades for fecha, hacerlo bien
    order_by = 'title'
    if (request.GET.has_key('template') and request.GET['template'] == 'novedades.html'):
        order_by = 'createdDate'

    contents = Contenido.objects.filter(categoria__id__exact=categoryId, publishContent=True).order_by(order_by)

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
    })

    templateName = 'listado-contenidos.html'
    if (request.GET.has_key('template') and request.GET['template'] != ''):
        templateName = request.GET['template']
    t = select_template(['home/{}'.format(templateName)])
    return HttpResponse(t.render(RequestContext(request, c)))


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

