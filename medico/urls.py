from django.conf.urls import patterns, include, url
from medico.views import get_disponibilidad_medicos, get_disponibilidad_medicos_json, get_disponibilidad, update_disponibilidad, delete_disponibilidad
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = patterns('',
    url(r'^api/medico/', include(router.urls)),
    url(r'^medicos/disponibilidad/', get_disponibilidad_medicos),
    url(r'^medicos/disponibilidad/json/', get_disponibilidad_medicos_json),
    url(r'^disponibilidad/$', get_disponibilidad),
    url(r'^disponibilidad/actualizar/$', update_disponibilidad),
    url(r'^disponibilidad/eliminar/$', delete_disponibilidad),
   )
