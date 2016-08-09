from django.conf.urls import patterns, include, url
from sendMail import *
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'', include('contenidos.urls')),
    (r'^sendMail/', sendMail),
    (r'', include('turno.urls')),
    (r'', include('paciente.urls')),
    (r'', include('comprobante.urls')),
    (r'', include('medico.urls')),
    (r'', include('usuario.urls')),
    (r'', include('estudio.urls')),
    (r'^admin/', include(admin.site.urls)),
)
