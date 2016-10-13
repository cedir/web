from django.conf.urls import include, url
from estudio.views import imprimir

urlpatterns = [
    url(r'^estudio/(?P<id_estudio>\d+)/imprimir/$', imprimir, name='estudio_imprimir'),
]

