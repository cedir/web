import smtplib
from django.conf import settings
from django.http import HttpResponse
from django.template import Template, Context, loader


def sendMail(request):
    import pdb; pdb.set_trace()
    toaddrs = settings.EMAIL_NOTIFICATION_ACCOUNTS
    subject = "Subject: Nuevo mensaje registrado desde cedirsalud.com.ar\n\n"
    request.content_type = "text/html"
    
    gmail_user = settings.EMAIL_ACCOUNT_USER
    gmail_pwd = settings.EMAIL_ACCOUNT_PSW

    name = request.POST['name']
    email = request.POST['email']
    tel = request.POST['tel']
    message = request.POST['message']

    msg = subject + 'Nombre: ' + name + "\n" + 'Mail: ' + email + "\n" + 'Tel: ' + tel + "\n" + 'Mensaje: ' + message + "\n"

    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    smtpserver.sendmail(gmail_user, toaddrs, msg)
    smtpserver.close()
    
    templateName = 'contacto_ok.html'
    t = loader.get_template('pages/' + templateName)
    
    c = Context({
        #'latest_poll_list': latest_poll_list,
	    #'current_date': now,
    })
    return HttpResponse(t.render(c))

