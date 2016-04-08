# -*- coding: utf-8
from django.conf.urls import patterns, include, url
from informe.views import ventas

urlpatterns = patterns('',
    url(r'^informe/ventas/(?P<responsable>\w+)/(?P<anio>\d{4})/(?P<mes>\d{2})/$', ventas),
)