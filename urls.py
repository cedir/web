from django.conf.urls import include, url
from sendMail import *
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'', include('contenidos.urls')),
    url(r'^sendMail/', sendMail),
    url(r'', include('turno.urls')),
    url(r'', include('paciente.urls')),
    url(r'', include('comprobante.urls')),
    url(r'', include('medico.urls')),
    url(r'', include('usuario.urls')),
    url(r'', include('estudio.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

