from django.conf.urls import include, url
from rest_framework import routers
from caja.views import MovimientoCajaViewSet

router = routers.SimpleRouter()
router.register(r'caja', MovimientoCajaViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
]