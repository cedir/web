from django.conf.urls import patterns, include, url
from estudio.views import imprimir, imprimir_nuevo

urlpatterns = patterns('',
    url(r'^estudio/(?P<id_estudio>\d+)/imprimir/$', imprimir, name='estudio_imprimir'),
    url(r'^estudio/(?P<id_estudio>\d+)/imprimir/nuevo/$', imprimir_nuevo, name='estudio_imprimir'),
)

