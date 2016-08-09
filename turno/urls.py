from django.conf.urls import patterns, include, url
from rest_framework import routers
from turno.views import anunciar, anular, reprogramar, confirmar, guardar, update, get_home, get_turno, get_buscar_turnos, get_turnos_disponibles, get_next_day_line, get_back_day_line, InfoTurnoViewSet


router = routers.DefaultRouter()
router.register(r'infoturno', InfoTurnoViewSet)

urlpatterns = patterns(
    '',
    url(r'^api/turno/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^turnos/$', get_home),
    url(r'^turnos/buscar/', get_buscar_turnos),
    url(r'^turnos/disponibles/', get_turnos_disponibles),
    url(r'^turnos/nextday/', get_next_day_line),
    url(r'^turnos/backday/', get_back_day_line),
    url(r'^turnos/guardar/', guardar),
    url(r'^turnos/(?P<id_turno>\d+)/anunciar/$', anunciar),
    url(r'^turnos/(?P<id_turno>\d+)/actualizar/$', update),
    url(r'^turnos/(?P<id_turno>\d+)/anular/$', anular),
    url(r'^turnos/(?P<id_turno>\d+)/reprogramar/$', reprogramar),
    url(r'^turnos/(?P<id_turno>\d+)/confirmar/$', confirmar),
    url(r'^turnos/(?P<id_turno>\d+)/$', get_turno),
)

