from django.conf.urls import patterns, include, url
from index import render_home
from contenidos.views import get_video

urlpatterns = patterns('',
    (r'^$', render_home),
    (r'^content/(\d+)/$', 'contenidos.getContent.getContent'),
    (r'^video/(?P<public_id>\w+={0,2})/$', get_video),
    (r'^static/', 'contenidos.getStatic.getStatic'),
    (r'^listContents/', 'contenidos.getContentsList.getList'),
    (r'^search/', 'contenidos.getSearchContents.getResults'),
    (r'balongastrico/', 'contenidos.getContent.getContent',{'idContent': 137, 'templateName': 'balon.html'}),
    (r'^endocapsula/$', 'contenidos.getContent.getContent',{'idContent': 2, 'templateName': 'endocapsula.html'}),
    (r'^videoendoscopia/$', 'contenidos.getContent.getContent',{'idContent': 65, 'templateName': 'videoendoscopia.html'}),
    (r'mapa-web/', 'contenidos.getStatic.getStatic',{'templateName': 'site-map.html'}),
    (r'^conferencias/$', 'contenidos.getContent.getContent',{'idContent': 94}),


    (r'^enlaces/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces.html'}),
    (r'enlaces/enlaces1.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces1.html'}),
    (r'enlaces/enlaces2.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces2.html'}),
    (r'enlaces/enlaces3.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces3.html'}),
    (r'enlaces/enlaces4.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces4.html'}),
    (r'enlaces/enlaces5.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces5.html'}),
    (r'enlaces/enlaces6.html/$', 'contenidos.getStatic.getStatic',{'templateName': 'enlaces6.html'}),

)
