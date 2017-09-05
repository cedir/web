from django.conf.urls import include, url
from anestesista.views import generar_vista_nuevo_pago


urlpatterns = [
    url(r'^api/anestesista/(?P<id_anestesista>\d+)/pago/(?P<anio>\d+)/(?P<mes>\d+)/$', generar_vista_nuevo_pago)
]

