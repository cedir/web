import os
import logging
import smtplib
from django.http import HttpResponse, Http404
from django.template import Template, Context, RequestContext
from django.template.loader import select_template
#from django.shortcuts import render
from contenidos.models import Contenido, Categoria
from estudio.models import Estudio


logger = logging.getLogger(u'videos')
NOVEDADES_CATEGORY_ID = 2

def get_home(request):

    slide_contents = Contenido.objects.filter(categoria__name__contains='Home slide', publishContent=True).order_by('publishInitDate')
    prep_estudios_contents = Contenido.objects.filter(categoria__name__contains='Preparaciones para estudio', publishContent=True).order_by('publishInitDate')[:3]
    departamentos = Contenido.objects.filter(categoria__name='Departamentos', publishContent=True).order_by('publishInitDate')[:10]
    novedades = Contenido.objects.filter(categoria__id__exact=NOVEDADES_CATEGORY_ID, publishContent=True).order_by("-createdDate")[:3]
    context = {
        u'novedades': novedades,
        u'slide_contents': slide_contents,
        u'preparacion_estudios_contents': prep_estudios_contents,
        u'departamentos_contents': departamentos,
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


def get_content(request, id_content, templateName='detalle-contenido.html'):
    if request.GET.has_key('template') and request.GET['template']:
        templateName = request.GET['template']

    content = Contenido.objects.get(pk=id_content)

    all_images = [content.img1, content.img2, content.img3]
    non_empty_parts = [os.path.splitext(p.name) for p in all_images if p]

    images = [(
        file_path_name + ext,
    ) for file_path_name, ext in non_empty_parts]

    context = Context({
        'id':content.id,
        'title':content.title,
        'description':content.description,
        'body':content.body,
        'footer':content.footer,
        'images': images,
        'page_title':content.title
    })

    template = select_template(['home/{}'.format(templateName)])
    return HttpResponse(template.render(RequestContext(request, context)))

def get_categoria_friendly_url(request, friendly_url):
    """
    Soporte para friendly URL: categoria/<friendly-url>
    """
    c_categ = Categoria.objects.filter(friendlyURL=friendly_url).first()
    if bool(c_categ):
        request.GET = request.GET.copy() #creamos una copia para poder mutarlo
        request.GET['categoryId'] = c_categ.id
        return get_categoria(request)
    else:
        raise Http404("No existe contenido: " + friendly_url)

def get_categoria(request):
    """
    muestra los contenidos de una Categoria
    """
    category_id = 1
    if request.GET.has_key('categoryId') and request.GET['categoryId']:
        category_id = request.GET['categoryId']

    #Parche para ordenar novedades for fecha, hacerlo bien
    order_by = 'id'
    if request.GET.has_key('template') and request.GET['template'] == 'novedades.html':
        order_by = 'createdDate'

    categoria = Categoria.objects.get(id=category_id)
    contents = Contenido.objects.filter(categoria__id__exact=category_id, publishContent=True).order_by(order_by)

    def create_content(content):
        """
        genera un contenido
        """

        contents_dicc = {
            "id" : content.id,
            "title": content.title,
            "description": content.description,
            "pub_date": content.publishInitDate or content.createdDate.date(),
            "url": content.friendlyURL or content.id,
            "categories": content.keywords.split(',') if content.keywords else [],
            "img1": content.img1,
            "footer": content.footer
            }

        if content.img1:
            file_path_name, ext = os.path.splitext(content.img1.name)
            contents_dicc["img1_min"] = file_path_name + '_min' + ext

        return contents_dicc

    context = Context({
        'title': categoria.name,
        'description': categoria.description,
        'friendly': categoria.friendlyURL,
        'contents': [create_content(content) for content in contents],
        })

    template_name = 'listado-contenidos.html'
    if request.GET.has_key('template') and request.GET['template']:
        template_name = request.GET['template']

    template = select_template(['home/{}'.format(template_name)])
    return HttpResponse(template.render(RequestContext(request, context)))


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

