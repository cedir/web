from django.conf.urls import include, url
from anestesista.views import generar_vista_nuevo_pago, AnastesistaViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'anestesista', AnastesistaViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api/anestesista/(?P<id_anestesista>\d+)/pago/(?P<anio>\d+)/(?P<mes>\d+)/$', generar_vista_nuevo_pago),
]

