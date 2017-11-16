from django.conf.urls import include, url
from rest_framework import routers
from obra_social.views import ObraSocialViewSet

router = routers.SimpleRouter()
router.register(r'obra_social', ObraSocialViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
]
