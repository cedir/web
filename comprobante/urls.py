from django.conf.urls import include, url
from comprobante.views import imprimir, ventas

urlpatterns = [
    url(r'^comprobante/imprimir/(?P<cae>\d+)/$', imprimir, name='comprobante_imprimir'),
    url(r'^comprobante/informe/ventas/(?P<responsable>\w+)/(?P<anio>\d{4})/(?P<mes>\d{2})/$', ventas, name='comprobante_informe_ventas'),
]

