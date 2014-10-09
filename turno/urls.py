from django.conf.urls import patterns, include, url
from turno.views import *

urlpatterns = patterns('',
    
    url(r'^turnos/anunciar/(?P<id_turno>\d+)/$', anunciar),
)
