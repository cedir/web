from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'', include('contenidos.urls')),
    url(r'', include('turno.urls')),
    url(r'', include('medicamento.urls')),
    url(r'', include('paciente.urls')),
    url(r'', include('comprobante.urls')),
    url(r'', include('presentacion.urls')),
    url(r'', include('medico.urls')),
    url(r'', include('anestesista.urls')),
    url(r'', include('usuario.urls')),
    url(r'', include('estudio.urls')),
    url(r'', include('caja.urls')),
    url(r'', include('obra_social.urls')),
    url(r'', include('practica.urls')),
    url(r'', include('security.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

