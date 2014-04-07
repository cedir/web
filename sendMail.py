import smtplib
from django.http import HttpResponse
from django.template import Template, Context, loader

def sendMail(request):
    
    toaddrs = ['cedirsalud@gmail.com', 'walterbrunetti@gmail.com',
               'jose.brunetti@gmail.com', 'recepcioncedir@gmail.com']
    #toaddrs = 'walterbrunetti@gmail.com'
    subject = "Subject: Nuevo mensaje registrado desde cedirsalud.com.ar\n\n"
    request.content_type = "text/html"
    
    #fromaddr = 'cedirsalud@gmail.com'
    gmail_user = 'cedirsalud@gmail.com'
    gmail_pwd = 'endocapsula'


    
    
    
    name = request.POST['name']
    email = request.POST['email']
    tel = request.POST['tel']
    message = request.POST['message']

    header = 'To:' + 'cedirsalud@gmail.com,walterbrunetti@gmail.com' + '\n' + 'From: ' + gmail_user + '\n' + subject
    msg = subject + 'Nombre: ' + name + "\n" + 'Mail: ' + email + "\n" + 'Tel: ' + tel + "\n" + 'Mensaje: ' + message + "\n"
    #msg = header + '\n this is test msg \n\n'

    
    #server = smtplib.SMTP('localhost')
    #server.sendmail(fromaddr, toaddrs, msg)
    #server.quit()
    
    
    
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