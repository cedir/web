from django.conf.urls import include, url
from usuario.views import entrar, salir, home
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    url(r'^usuario/entrar/$', entrar, name='entrar'),
    url(r'^usuario/salir/$', salir, name='salir'),
    url(r'^usuario/home/$', home, name='home'),
    url(r'^api/usuario/get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
]

