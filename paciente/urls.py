from django.conf.urls import patterns, url
from paciente.views import create_form, update_form, create, update, buscar_form

urlpatterns = patterns(
    '',
    url(r'^paciente/$', create_form),
    url(r'^paciente/nuevo/$', create),
    url(r'^paciente/buscar/$', buscar_form),
    url(r'^paciente/(?P<id_paciente>\d+)/$', update_form),
    url(r'^paciente/(?P<id_paciente>\d+)/actualizar/$', update)
)
