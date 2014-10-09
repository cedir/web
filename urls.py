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
    (r'^turnos/$', getLogin),
    (r'balongastrico/', 'contenidos.getContent.getContent',{'idContent': 90, 'templateName': 'balon.html'}),
    (r'^endocapsula/$', 'contenidos.getContent.getContent',{'idContent': 2, 'templateName': 'endocapsula.html'}),
    (r'^videoendoscopia/$', 'contenidos.getContent.getContent',{'idContent': 65, 'templateName': 'videoendoscopia.html'}),
    (r'mapa-web/', 'contenidos.getStatic.getStatic',{'templateName': 'site-map.html'}),
    (r'^conferencias/$', 'contenidos.getContent.getContent',{'idContent': 94}),


    (r'', include('turno.urls')),

    
    (r'^enlaces/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces.html'}),
    (r'enlaces/enlaces1.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces1.html'}),
    (r'enlaces/enlaces2.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces2.html'}),
    (r'enlaces/enlaces3.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces3.html'}),
    (r'enlaces/enlaces4.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces4.html'}),
    (r'enlaces/enlaces5.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces5.html'}),
    (r'enlaces/enlaces6.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces6.html'}),
    
    
    # Uncomment this for admin:
    #(r'^admin/', include('django.contrib.admin.urls')),
    (r'^admin/', include(admin.site.urls)),

)
