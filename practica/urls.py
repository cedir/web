from django.conf.urls import include, url
from practica.views import PracticaViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'practica', PracticaViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls))
]