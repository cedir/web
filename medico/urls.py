from django.conf.urls import patterns, include, url
from medico.views import get_disponibilidad_medicos, get_disponibilidad_medico, get_disponibilidad, create_disponibilidad, update_disponibilidad, delete_disponibilidad
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = patterns('',
    url(r'^api/medico/', include(router.urls)),
    url(r'^medico/disponibilidad/$', get_disponibilidad_medicos),
    url(r'^medico/(?P<id_medico>\d+)/disponibilidad/$', get_disponibilidad_medico),
    url(r'^disponibilidad/$', create_disponibilidad),
    url(r'^disponibilidad/(?P<id_disponibilidad>\d+)/$', get_disponibilidad),
    url(r'^disponibilidad/(?P<id_disponibilidad>\d+)/actualizar/$', update_disponibilidad),
    url(r'^disponibilidad/(?P<id_disponibilidad>\d+)/eliminar/$', delete_disponibilidad),
   )
