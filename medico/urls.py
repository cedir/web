from django.conf.urls import include, url
from medico.views import MedicoViewSet, get_disponibilidad_medico, get_disponibilidad_medicos, get_disponibilidad, \
    create_disponibilidad, update_disponibilidad, delete_disponibilidad, PagoMedicoViewList
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'medico', MedicoViewSet)
router.register(r'pago-medico', PagoMedicoViewList)

urlpatterns = [
    url(r'^medico/(?P<id_medico>\d+)/disponibilidad/$', get_disponibilidad_medico),
    url(r'^disponibilidad/$', get_disponibilidad_medicos),
    url(r'^disponibilidad/nueva/$', create_disponibilidad),
    url(r'^disponibilidad/(?P<id_disponibilidad>\d+)/$', get_disponibilidad),
    url(r'^disponibilidad/(?P<id_disponibilidad>\d+)/actualizar/$', update_disponibilidad),
    url(r'^disponibilidad/(?P<id_disponibilidad>\d+)/eliminar/$', delete_disponibilidad),
    url(r'^api/', include(router.urls))
]
