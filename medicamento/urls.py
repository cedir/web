from django.conf.urls import include, url
from medicamento.views import MedicamentoViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'medicamento', MedicamentoViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
]