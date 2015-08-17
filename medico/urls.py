from django.conf.urls import patterns, include, url
from rest_framework import routers
from medico.views import InfoMedicoViewSet

router = routers.DefaultRouter()
router.register(r'infomedicos', InfoMedicoViewSet)

urlpatterns = patterns('',
    
    url(r'^api/medico/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
