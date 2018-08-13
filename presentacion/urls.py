from django.conf.urls import include, url
from rest_framework import routers
from presentacion.views import PresentacionViewSet

router = routers.SimpleRouter()
router.register(r'presentacion', PresentacionViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
]
