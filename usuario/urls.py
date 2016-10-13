from django.conf.urls import include, url
from usuario.views import entrar, salir, home

urlpatterns = [
    url(r'^usuario/entrar/$', entrar, name='entrar'),
    url(r'^usuario/salir/$', salir, name='salir'),
    url(r'^usuario/home/$', home, name='home'),
]

