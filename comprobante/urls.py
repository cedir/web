from django.conf.urls import patterns, include, url
from comprobante.views import imprimir

urlpatterns = patterns('',
    url(r'^comprobante/imprimir/(?P<cae>\d+)/$', imprimir),
)
