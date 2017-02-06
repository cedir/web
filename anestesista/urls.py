from django.conf.urls import include, url
from anestesista.views import pago


urlpatterns = [
    url(r'^api/anestesista/(?P<id_anestesista>\d+)/pago/(?P<anio>\d+)/(?P<mes>\d+)/$', pago)
]