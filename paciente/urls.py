from django.conf.urls import patterns, url
from paciente.views import get_create, get_update, post_create, post_update, get_buscar

urlpatterns = patterns(
    '',
    url(r'^paciente/$', get_create),
    url(r'^paciente/nuevo/$', post_create),
    url(r'^paciente/buscar/$', get_buscar),
    url(r'^paciente/(?P<id_paciente>\d+)/$', get_update),
    url(r'^paciente/(?P<id_paciente>\d+)/actualizar/$', post_update)
)
