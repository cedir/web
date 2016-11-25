from django.conf.urls import url
#from index import render_home
from contenidos.views import get_video, send_mail, get_home, get_list_content, get_content, get_content_friendly_url
from contenidos.getStatic import getStatic
#from contenidos.getContent import getContent
#from contenidos.getContentsList import getList
from contenidos.getSearchContents import getResults


urlpatterns = [
    url(r'^$', get_home),
    url(r'^content/(\d+)/$', get_content),
    url(r'^content/([\w-]+)/$', get_content_friendly_url),
    url(r'^sendMail/', send_mail),
    url(r'^static/', getStatic),
    url(r'^listContents/', get_list_content),
    url(r'^search/', getResults),
    url(r'^video/(?P<public_id>\w+={0,2})/$', get_video),

    # TODO: estas urls hay que dejarlas por compatibilidad con la base de google, aunque se le puede sacar el template.
    url(r'balongastrico/', get_content,{'idContent': 137, 'templateName': 'balon.html'}),
    url(r'^endocapsula/$', get_content,{'idContent': 2, 'templateName': 'endocapsula.html'}),
    url(r'^videoendoscopia/$', get_content,{'idContent': 65, 'templateName': 'videoendoscopia.html'}),
    url(r'mapa-web/', getStatic,{'templateName': 'site-map.html'}),
    url(r'^conferencias/$', get_content,{'idContent': 94}),

    # TODO: esto vuela, pero hay que volar tambien los html asociados
    url(r'^enlaces/$', getStatic,{'templateName': 'enlaces.html'}),
    url(r'enlaces/enlaces1.html/$', getStatic,{'templateName': 'enlaces1.html'}),
    url(r'enlaces/enlaces2.html/$', getStatic,{'templateName': 'enlaces2.html'}),
    url(r'enlaces/enlaces3.html/$', getStatic,{'templateName': 'enlaces3.html'}),
    url(r'enlaces/enlaces4.html/$', getStatic,{'templateName': 'enlaces4.html'}),
    url(r'enlaces/enlaces5.html/$', getStatic,{'templateName': 'enlaces5.html'}),
    url(r'enlaces/enlaces6.html/$', getStatic,{'templateName': 'enlaces6.html'}),
]

