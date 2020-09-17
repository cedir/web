
# -*- coding: utf-8 -*-
from PIL import Image
import glob
import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


IMG_MAX_SIZE = 700 * 1024  # 700 kB
IMG_MIN_SIZE = 10 * 1024  # 10 kB
IMG_MIN_WIDTH = 40  # pixels
IMG_MIN_HEIGHT = 40  # pixels


def validate_friendly_url(url, instance):
    if not url:
        return
    if ' ' in url:
        raise ValidationError("La URL friendlyURL no puede contener espacios")
    try:
        url.decode('ascii')
    except UnicodeEncodeError:
        raise ValidationError("La URL friendlyURL no puede contener caracteres con acentos o eñes")
    try:
        instance._meta.model.objects.exclude(id=instance.id).get(friendlyURL=url)
        raise ValidationError("Ya existe otro contenido con la misma friendlyURL ingresada. Solo puede haber 1.")
    except instance._meta.model.DoesNotExist:
        pass  ## all good

# Create your models here.
class Categoria(models.Model):
    name = models.CharField("Nombre",max_length=200, null=False,blank=False)
    description = models.TextField("Descripcion",blank=True)
    friendlyURL = models.CharField("Friendly URL", max_length=100,null=True,blank=True)

    def __unicode__ (self):
        return self.name

    def clean(self):
        validate_friendly_url(self.friendlyURL, self)


class Contenido(models.Model):
    title = models.CharField("Titulo", max_length=200,null=False,blank=False )
    description = models.TextField("Resumen",null=False,blank=False)
    body = models.TextField("Desarrollo",blank=True)
    publishInitDate = models.DateField("Inicio de publicacion",null=True,blank=True)
    publishEndDate = models.DateField("Fin de publicacion",null=True,blank=True)
    publishContent = models.BooleanField("Publicar contenido",default=True)
    destacarContent = models.BooleanField("Destacar contenido",default=False)
    img1 = models.ImageField("Imagen principal",upload_to='uploads_imgs', blank=True)
    img2 = models.ImageField("Imagen 2",upload_to='uploads_imgs', blank=True)
    img3 = models.ImageField("Imagen 3",upload_to='uploads_imgs', blank=True)
    footer = models.TextField("Pie",blank=True)
    friendlyURL = models.CharField("Friendly URL", max_length=100,null=True,blank=True)
    keywords = models.CharField("Keywords", max_length=100,null=True,blank=True)
    categoria = models.ManyToManyField(Categoria, verbose_name="Categoria")
    createdDate = models.DateTimeField("Creado",null=True,blank=True,auto_now_add=True)
    updated = models.DateTimeField(editable=False, null=True, auto_now=True)

    @property
    def fecha_display(self):
        if self.publishInitDate:
            return self.publishInitDate.strftime('%d/%m/%Y')
        return self.createdDate.strftime('%d/%m/%Y')

    @property
    def url(self):
        return '/content/{}'.format(self.friendlyURL) if self.friendlyURL else '/content/{}'.format(self.id)

    def validate_image(self, image):
        #imgPath = settings.MEDIA_ROOT + self.img1.name
        #im = Image.open(imgPath)
        #filePathName, ext = os.path.splitext(imgPath)
        #width, height = im.size

        if image.size < IMG_MIN_SIZE:
            raise ValidationError("La imagen es menor a 10 kB que es el tamanio minimo permitido")
        if image.size > IMG_MAX_SIZE:
            raise ValidationError("La imagen es mayor a 700 kB que es el tamanio maximo permitido")
        if image.width < IMG_MIN_WIDTH:
            raise ValidationError("Error: imagen es muy chica: {} px que es el tamanio minimo para el ancho".format(IMG_MIN_WIDTH))
        if image.height < IMG_MIN_HEIGHT:
            raise ValidationError("Error: imagen es muy chica: {} px que es el tamanio minimo para el alto".format(IMG_MIN_HEIGHT))

    def clean(self):

        if self.img1.name != '':
            self.validate_image(self.img1)
        if self.img2.name != '':
            self.validate_image(self.img2)
        if self.img3.name != '':
            self.validate_image(self.img3)

        validate_friendly_url(self.friendlyURL, self)

    def __unicode__ (self):
        return self.title
