from django.conf.urls import include, url
from comprobante.views import imprimir, ventas, InformeMensualView, ComprobanteViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'comprobante', ComprobanteViewSet, base_name='Comprobante')

urlpatterns = [
    url(r'^comprobante/imprimir/(?P<cae>\d+)/$', imprimir, name='comprobante_imprimir'),
    url(r'^comprobante/informe/ventas/(?P<responsable>\w+)/(?P<anio>\d{4})/(?P<mes>\d{2})/$', ventas, name='comprobante_informe_ventas'),
    url(r'^api/comprobantes', InformeMensualView.as_view()),
    url(r'^api/', include(router.urls)),
]
