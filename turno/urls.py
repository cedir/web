from django.conf.urls import include, url
from rest_framework import routers
from turno.views import anunciar, anular, reprogramar, confirmar, guardar, update, get_home, get_turno, get_buscar_turnos, get_turnos_disponibles, get_next_day_line, get_back_day_line, InfoTurnoViewSet, TurnoViewSet


router = routers.SimpleRouter()
router.register(r'infoturno', InfoTurnoViewSet)
router2 = routers.SimpleRouter()
router2.register(r'turnos', TurnoViewSet)

urlpatterns = [
    url(r'^api/turno/', include(router.urls)),
    url(r'^api/', include(router2.urls)),
    url(r'^turnos/$', get_home),
    url(r'^turno/buscar/', get_buscar_turnos),
    url(r'^turno/disponibles/', get_turnos_disponibles),
    url(r'^turno/nextday/', get_next_day_line),
    url(r'^turno/backday/', get_back_day_line),
    url(r'^turno/guardar/', guardar),
    url(r'^turno/(?P<id_turno>\d+)/anunciar/$', anunciar),
    url(r'^turno/(?P<id_turno>\d+)/actualizar/$', update),
    url(r'^turno/(?P<id_turno>\d+)/anular/$', anular),
    url(r'^turno/(?P<id_turno>\d+)/reprogramar/$', reprogramar),
    url(r'^turno/(?P<id_turno>\d+)/confirmar/$', confirmar),
    url(r'^turno/(?P<id_turno>\d+)/$', get_turno),
]

