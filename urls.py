from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
from index import *
from sendMail import *
from dispatcher import *

from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    # Example:
    # (r'^cedir/', include('cedir.foo.urls')),
    
    (r'^$', render_home),
    #(r'^$', get_message),
    (r'^content/(\d+)/$', 'contenidos.getContent.getContent'),
    (r'^static/', 'contenidos.getStatic.getStatic'),
    (r'^listContents/', 'contenidos.getContentsList.getList'),
    (r'^search/', 'contenidos.getSearchContents.getResults'),
    (r'^sendMail/', sendMail),
    (r'^app/', dispatch),
    (r'^turnos/', getLogin),
    (r'balongastrico/', 'contenidos.getContent.getContent',{'idContent': 90, 'templateName': 'balon.html'}),
    (r'^endocapsula/$', 'contenidos.getContent.getContent',{'idContent': 2, 'templateName': 'endocapsula.html'}),
    (r'^videoendoscopia/$', 'contenidos.getContent.getContent',{'idContent': 65, 'templateName': 'videoendoscopia.html'}),
    (r'mapa-web/', 'contenidos.getStatic.getStatic',{'templateName': 'site-map.html'}),
    (r'^conferencias/$', 'contenidos.getContent.getContent',{'idContent': 94}),
    
    (r'^enlaces/', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces.html'}),
    (r'enlaces/1/', 'contenidos.getStatic.getStatic',{'templateName': 'enlace1.html'}),
    (r'enlaces/2/', 'contenidos.getStatic.getStatic',{'templateName': 'enlace2.html'}),
    (r'enlaces/3/', 'contenidos.getStatic.getStatic',{'templateName': 'enlace3.html'}),
    (r'enlaces/4/', 'contenidos.getStatic.getStatic',{'templateName': 'enlace4.html'}),
    (r'enlaces/5/', 'contenidos.getStatic.getStatic',{'templateName': 'enlace5.html'}),
    (r'enlaces/6/', 'contenidos.getStatic.getStatic',{'templateName': 'enlace6.html'}),
    
    
    # Uncomment this for admin:
    #(r'^admin/', include('django.contrib.admin.urls')),
    (r'^admin/', include(admin.site.urls)),

)