from django.conf.urls import include, url
from rest_framework import routers
from estudio.views import imprimir, add_default_medicacion, EstudioViewSet, MedicacionViewSet

router = routers.SimpleRouter()
router.register(r'estudio', EstudioViewSet)
router.register(r'medicacion', MedicacionViewSet)


urlpatterns = [
    url(r'^estudio/(?P<id_estudio>\d+)/imprimir/$', imprimir, name='estudio_imprimir'),
    url(r'^api/estudio/add-default-medicacion', add_default_medicacion),
    url(r'^api/', include(router.urls)),
]
