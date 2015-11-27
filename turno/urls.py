from django.conf.urls import patterns, include, url
from rest_framework import routers
from turno.views import anunciar, InfoTurnoViewSet


router = routers.DefaultRouter()
router.register(r'infoturno', InfoTurnoViewSet)

urlpatterns = patterns('',
    url(r'^api/turno/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^turnos/anunciar/(?P<id_turno>\d+)/$', anunciar),
)

