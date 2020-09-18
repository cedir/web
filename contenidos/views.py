# coding: utf-8
import os
import logging
import smtplib
import settings
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from datetime import date
from django.http import HttpResponse, Http404
from django.template.loader import select_template
from django.db.models import  Value
from django.db.models.functions import Coalesce

#from django.shortcuts import render
from contenidos.models import Contenido, Categoria
from estudio.models import Estudio

from email.mime.text import MIMEText

logger = logging.getLogger('videos')
NOVEDADES_CATEGORY_ID = 2

def get_home(request):

    slide_contents = Contenido.objects.filter(categoria__name__contains='Home slide', publishContent=True).annotate(publishinitdate_null=Coalesce('publishInitDate', Value(date.min))).order_by('-publishinitdate_null')
    preguntas_frecuentes_contents = Contenido.objects.filter(categoria__name__contains='nos preguntan nuestros pacientes', publishContent=True).annotate(publishinitdate_null=Coalesce('publishInitDate', Value(date.min))).order_by('-publishinitdate_null')[:4]
    enfermedades_digestivas_contents = Contenido.objects.filter(categoria__name__contains='Enfermedades Digestivas', publishContent=True).annotate(publishinitdate_null=Coalesce('publishInitDate', Value(date.min))).order_by('-publishinitdate_null')[:4]
    unidades = Contenido.objects.filter(categoria__name='Unidades', publishContent=True).annotate(publishinitdate_null=Coalesce('publishInitDate', Value(date.min))).order_by('-publishinitdate_null')[:10]
    novedades = Contenido.objects.filter(categoria__id__exact=NOVEDADES_CATEGORY_ID, publishContent=True).annotate(publishinitdate_null=Coalesce('publishInitDate', Value(date.min))).order_by("-publishinitdate_null")[:3]
    context = {
        'novedades': novedades,
        'slide_contents': slide_contents,
        'enfermedades_digestivas_contents': enfermedades_digestivas_contents,
        'unidades_contents': unidades,
        'preguntas_frecuentes_contents': preguntas_frecuentes_contents,
    }
    t = select_template(['home/index.html'])
    return HttpResponse(t.render(context))

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
    if 'template' in request.GET and request.GET['template']:
        templateName = request.GET['template']

    content = Contenido.objects.get(pk=id_content)
    categorias_id = [c.id for c in content.categoria.all()]
    related = Contenido.objects.filter(categoria__in=categorias_id).exclude(pk=id_content).distinct().order_by('-createdDate')[:3]

    def get_images(c_content):
        all_images = [c_content.img1, c_content.img2, c_content.img3]
        non_empty_parts = [os.path.splitext(p.name) for p in all_images if p]

        return [(
            file_path_name + ext,
        ) for file_path_name, ext in non_empty_parts]

    context = {
        'id':content.id,
        'title':content.title,
        'description':content.description,
        'keywords':content.keywords,
        'body':content.body,
        'footer':content.footer,
        'images': get_images(content),
        'page_title':content.title,
        'related': [{
            'title': r.title,
            'description': r.description,
            'url': r.friendlyURL or r.id,
            'images': get_images(r)
        } for r in related]
    }

    template = select_template(['home/{}'.format(templateName)])
    return HttpResponse(template.render(context))

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
    if 'categoryId' in request.GET and request.GET['categoryId']:
        category_id = request.GET['categoryId']

    categoria = Categoria.objects.get(id=category_id)
    contents = Contenido.objects.filter(categoria__id__exact=category_id, publishContent=True).annotate(publishinitdate_null=Coalesce('publishInitDate', Value(date.min))).order_by("-publishinitdate_null", "-id")[:15]

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

    context = {
        'title': categoria.name,
        'description': categoria.description,
        'friendly': categoria.friendlyURL,
        'contents': [create_content(content) for content in contents],
        }

    template_name = 'listado-contenidos.html'
    if 'template' in request.GET and request.GET['template']:
        template_name = request.GET['template']

    template = select_template(['home/{}'.format(template_name)])
    return HttpResponse(template.render(context))

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
        'video_url': video_url,
        'paciente': paciente,
        'fecha_vencimiento': fecha_vencimiento,
        'link_vencido': link_vencido,
        'estudio_does_not_exist': estudio_does_not_exist,
    }
    t = select_template(['pages/video_details.html'])
    return HttpResponse(t.render(context))

def send_mail(request):
    data = { 'sent': 'no' }

    try:
        toaddrs = settings.EMAIL_NOTIFICATION_ACCOUNTS
        gmail_user = settings.EMAIL_ACCOUNT_USER
        gmail_pwd = settings.EMAIL_ACCOUNT_PSW

        #valida captcha
        captcha = request.POST['captcha']


        greq = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify')
        greq.data = urllib.parse.urlencode({ 'secret': settings.CAPTCHA_SECRET, 'response': captcha })

        gres = urllib.request.urlopen(greq)
        gdata = json.load(gres)

        if gdata['success']:
            name = request.POST['name']
            email = request.POST['email']
            tel = request.POST['tel']
            message = request.POST['message']

            text = 'Nombre: ' + name + "\n" + 'Mail: ' + email + "\n" + 'Tel: ' + tel + "\n" + 'Mensaje: ' + message + "\n"
            msg = MIMEText(text.encode('utf-8'), _charset='utf-8')
            msg['Subject'] = "Nuevo mensaje registrado desde cedirsalud.com.ar"
            msg['From'] = gmail_user
            msg['To'] = ','.join(toaddrs)

            smtpserver = smtplib.SMTP("smtp.gmail.com",587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(gmail_user, gmail_pwd)
            smtpserver.sendmail(gmail_user, toaddrs, msg.as_string())
            smtpserver.close()

            data = { 'sent': 'yes' }
    except:
        pass

    return HttpResponse(json.dumps(data), content_type = "application/json")
