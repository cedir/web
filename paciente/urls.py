from django.conf.urls import patterns, url
from paciente.views import get_create, get_update, get_buscar

urlpatterns = patterns(
    '',
    url(r'^paciente/nuevo/', get_create),
    url(r'^paciente/buscar/', get_buscar),
    url(r'^paciente/(?P<id_paciente>\d+)/editar/$', get_update)
)
