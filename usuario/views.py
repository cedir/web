# -*- coding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from datetime import datetime

# Create your views here.
def entrar(request):
    context = {}
    error_message = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if "next" in request.GET:
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    return HttpResponseRedirect(reverse('home'))
            else:
                logout(request)
                error_message = 'Usuario deshabilitado'
        else:
            logout(request)
            error_message = 'Usuario/Contraseña inválidos'

    context.update({'user': request.user})

    if error_message:
        context.update({'error_message': error_message})

    return render(request, 'usuario/entrar.html', context)


def salir(request):
    logout(request)

    if "next" in request.GET:
        target = request.GET["next"]
    else:
        target = reverse('entrar')

    return HttpResponseRedirect(target)


def home(request):
    if not request.user.is_anonymous():
        now = datetime.now()
        context = {
            'responsables': [('Cedir', 'cedir'), ('Brunetti', 'brunetti')],
            'years': [('{0:04}'.format(year), year == now.year) for year in range(now.year - 1, now.year + 2)],
            'months': [('{0:02}'.format(month), month == now.month) for month in range(1, 13)],
            'user': request.user,
        }
        return render(request, 'usuario/home.html', context)
    else:
        return HttpResponseRedirect(reverse('entrar'))
