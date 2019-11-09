from django.conf.urls import include, url
from comprobante.views import imprimir, ventas, crear_asociado, InformeMensualView, ComprobanteViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'comprobante', ComprobanteViewSet)

urlpatterns = [
    url(r'^comprobante/imprimir/(?P<cae>\d+)/$', imprimir, name='comprobante_imprimir'),
    url(r'^comprobante/informe/ventas/(?P<responsable>\w+)/(?P<anio>\d{4})/(?P<mes>\d{2})/$', ventas, name='comprobante_informe_ventas'),
    url(r'^api/comprobantes', InformeMensualView.as_view()),
    url(r'^api/', include(router.urls)),
]
