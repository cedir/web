from django.conf.urls import patterns, include, url
from contenidos.views import get_home

urlpatterns = patterns('',
    (r'^$', get_home),
)
