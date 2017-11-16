from django.conf.urls import include, url
from rest_framework import routers
from estudio.views import imprimir, EstudioViewSet, EstudioList

router = routers.SimpleRouter()
router.register(r'estudio', EstudioViewSet)


urlpatterns = [
    url(r'^estudio/(?P<id_estudio>\d+)/imprimir/$', imprimir, name='estudio_imprimir'),
    url('^estudio/(?P<id_estudio>.+)/$', EstudioList.as_view()),
    url(r'^api/', include(router.urls)),
]
