
from PIL import Image
import glob
import os
from django.db import models
from django.conf import settings


# Create your models here.
class Categoria(models.Model):
    name = models.CharField("Nombre",max_length=200, null=False,blank=False)
    description = models.TextField("Descripcion",blank=True)
    
    def __unicode__ (self):
        return self.name

    class Admin:
        list_display = ('name', 'description')
        search_fields = ['name']


class Contenido(models.Model):
    title = models.CharField("Titulo", max_length=200,null=False,blank=False )
    description = models.TextField("Resumen",null=False,blank=False)
    body = models.TextField("Desarrollo",blank=True)
    createdDate = models.DateTimeField("Creado",null=True,blank=True,auto_now_add=True)
    publishInitDate = models.DateField("Inicio de publicacion",null=True,blank=True)
    publishEndDate = models.DateField("Fin de publicacion",null=True,blank=True)
    publishContent = models.BooleanField("Publicar contenido",default=True)
    destacarContent = models.BooleanField("Destacar contenido",default=False)
    img1 = models.ImageField("Imagen principal",upload_to='uploads_imgs', blank=True)
    img2 = models.ImageField("Imagen 2",upload_to='uploads_imgs', blank=True)
    img3 = models.ImageField("Imagen 3",upload_to='uploads_imgs', blank=True)
    footer = models.TextField("Pie",blank=True)
    friendlyURL = models.CharField("Friendly URL", max_length=100,null=True,blank=True)
    categoria = models.ManyToManyField(Categoria, verbose_name="Categoria")

    @property
    def url(self):
        return self.friendlyURL if self.friendlyURL else '/content/{}'.format(self.id)
    
    def save(self):
        super(Contenido, self).save()

        minSizes = [147,140]
        medSizes = [200,200]

        #f = open('/tmp/w.w','w')
        #TODO: checkear que no hay otra imagen con el mismo nombre y renomabrar, si es que no lo hace PIL automaticamente

        if self.img1.name <> '':
            imgPath = settings.MEDIA_ROOT + self.img1.name
            im = Image.open(imgPath)
            filePathName, ext = os.path.splitext(imgPath)
            imgSize = im.size

            #min image
            #if (imgSize[0] > minSizes[0]) or (imgSize[1] > minSizes[1]):
            #    #f.write('La que lo pario2: ' + self.img2.name )
            #    im.thumbnail(minSizes, Image.ANTIALIAS)
            #    im.save(filePathName + '_min' + ext, "JPEG")

            #med image
            #if (imgSize[0] > medSizes[0]) or (imgSize[1] > medSizes[1]):
            #    imCopy = Image.open(imgPath)
            #    imCopy.thumbnail(medSizes, Image.ANTIALIAS)
            #    imCopy.save(filePathName + '_med' + ext, "JPEG")

        if self.img2.name <> '':
            imgPath = settings.MEDIA_ROOT + self.img2.name
            im = Image.open(imgPath)
            filePathName, ext = os.path.splitext(imgPath)
            imgSize = im.size

            #med image
            if (imgSize[0] > medSizes[0]) or (imgSize[1] > medSizes[1]):
                im.thumbnail(medSizes, Image.ANTIALIAS)
                im.save(filePathName + '_med' + ext, "JPEG")

        if self.img3.name <> '':
            imgPath = settings.MEDIA_ROOT + self.img3.name
            im = Image.open(imgPath)
            filePathName, ext = os.path.splitext(imgPath)
            imgSize = im.size

            #med image
            if (imgSize[0] > medSizes[0]) or (imgSize[1] > medSizes[1]):
                im.thumbnail(medSizes, Image.ANTIALIAS)
                im.save(filePathName + '_med' + ext, "JPEG")
        #f.close()

    def __unicode__ (self):
        return self.title

    class Admin:
        list_display = ('title', 'description', 'createdDate', 'publishContent' )
        list_filter = ['publishContent']
        search_fields = ['title', 'description']
