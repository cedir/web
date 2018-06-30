from django.conf.urls import url, include
from paciente.views import PacienteViewSet, create_form, update_form, create, update, buscar_form
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'paciente', PacienteViewSet)

urlpatterns = [
    url(r'^paciente/$', create_form),
    url(r'^paciente/nuevo/$', create),
    url(r'^paciente/buscar/$', buscar_form),
    url(r'^paciente/(?P<id_paciente>\d+)/$', update_form),
    url(r'^paciente/(?P<id_paciente>\d+)/actualizar/$', update),
    url(r'^api/', include(router.urls)),
]
