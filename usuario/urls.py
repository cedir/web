from django.conf.urls import patterns, url
from usuario.views import entrar, salir, home

urlpatterns = patterns('',
    url(r'^usuario/entrar/$', entrar, name='entrar'),
    url(r'^usuario/salir/$', salir, name='salir'),
    url(r'^usuario/home/$', home, name='home'),
)
