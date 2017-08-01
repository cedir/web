from django.conf.urls import include, url
from security.views import obtain_auth_token


urlpatterns = [
    url(r'^security/auth/$', obtain_auth_token),
]

