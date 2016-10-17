from django.conf.urls import url
#from index import render_home
from contenidos.views import get_video, send_mail, get_home
from contenidos.getStatic import getStatic
from contenidos.getContent import getContent
from contenidos.getContentsList import getList
from contenidos.getSearchContents import getResults


urlpatterns = [
    url(r'^$', get_home),
    url(r'^content/(\d+)/$', getContent),
    url(r'^sendMail/', send_mail),
    url(r'^video/(?P<public_id>\w+={0,2})/$', get_video),
    url(r'^static/', getStatic),
    url(r'^listContents/', getList),
    url(r'^search/', getResults),
    url(r'balongastrico/', getContent,{'idContent': 137, 'templateName': 'balon.html'}),
    url(r'^endocapsula/$', getContent,{'idContent': 2, 'templateName': 'endocapsula.html'}),
    url(r'^videoendoscopia/$', getContent,{'idContent': 65, 'templateName': 'videoendoscopia.html'}),
    url(r'mapa-web/', getStatic,{'templateName': 'site-map.html'}),
    url(r'^conferencias/$', getContent,{'idContent': 94}),


    url(r'^enlaces/$', getStatic,{'templateName': 'enlaces.html'}),
    url(r'enlaces/enlaces1.html/$', getStatic,{'templateName': 'enlaces1.html'}),
    url(r'enlaces/enlaces2.html/$', getStatic,{'templateName': 'enlaces2.html'}),
    url(r'enlaces/enlaces3.html/$', getStatic,{'templateName': 'enlaces3.html'}),
    url(r'enlaces/enlaces4.html/$', getStatic,{'templateName': 'enlaces4.html'}),
    url(r'enlaces/enlaces5.html/$', getStatic,{'templateName': 'enlaces5.html'}),
    url(r'enlaces/enlaces6.html/$', getStatic,{'templateName': 'enlaces6.html'}),
]

