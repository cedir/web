# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Nombre')),
                ('description', models.TextField(verbose_name=b'Descripcion', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contenido',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Titulo')),
                ('description', models.TextField(verbose_name=b'Resumen')),
                ('body', models.TextField(verbose_name=b'Desarrollo', blank=True)),
                ('createdDate', models.DateTimeField(auto_now_add=True, verbose_name=b'Creado', null=True)),
                ('publishInitDate', models.DateField(null=True, verbose_name=b'Inicio de publicacion', blank=True)),
                ('publishEndDate', models.DateField(null=True, verbose_name=b'Fin de publicacion', blank=True)),
                ('publishContent', models.BooleanField(default=True, verbose_name=b'Publicar contenido')),
                ('destacarContent', models.BooleanField(default=False, verbose_name=b'Destacar contenido')),
                ('img1', models.ImageField(upload_to=b'uploads_imgs', verbose_name=b'Imagen principal', blank=True)),
                ('img2', models.ImageField(upload_to=b'uploads_imgs', verbose_name=b'Imagen 2', blank=True)),
                ('img3', models.ImageField(upload_to=b'uploads_imgs', verbose_name=b'Imagen 3', blank=True)),
                ('footer', models.TextField(verbose_name=b'Pie', blank=True)),
                ('friendlyURL', models.CharField(max_length=100, null=True, verbose_name=b'Friendly URL', blank=True)),
                ('categoria', models.ManyToManyField(to='contenidos.Categoria', verbose_name=b'Categoria')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
