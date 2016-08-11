from django.conf.urls import patterns, url
from estudio.views import imprimir

urlpatterns = patterns('',
    url(r'^estudio/(?P<id_estudio>\d+)/imprimir/$', imprimir, name='estudio_imprimir'),
)

