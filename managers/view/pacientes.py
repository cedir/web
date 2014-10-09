# -*- coding: utf-8 -*-
from django.template import Template, Context, loader
from datetime import datetime


class ViewPacientes():

    def __init__(self, request=None):
        self.request = request

    def getCreate(self):
        c = Context({
          'isCreate':1,
          'logged_user_name':self.request.session["cedir_user_name"],
        })
        t = loader.get_template('turnos/ABMPaciente.html')
        return t.render(c)

    def getUpdate(self, paciente):
        fechaNacimiento = ""
        if (paciente.fechaNacimiento is not None):
            fechaNacimiento = paciente.fechaNacimiento.strftime("%d/%m/%Y")

        c = Context({
          u'id': paciente.id,
          u'dni': paciente.dni,
          u'nombre': paciente.nombre,
          u'apellido': paciente.apellido,
          u'domicilio': paciente.domicilio,
          u'telefono': paciente.telefono,
          u'fechaNacimiento': fechaNacimiento,
          u'sexo': paciente.sexo,
          u'nro_afiliado': paciente.nroAfiliado,
          u'email': paciente.email or u'',
          u'logged_user_name': self.request.session["cedir_user_name"],
        })

        t = loader.get_template('turnos/ABMPaciente.html')
        return t.render(c)

    def getBuscar(self, **kwargs):
        dni = kwargs['dni']
        apellido = kwargs['apellido']
        pacientes = kwargs['pacientes']
        requestType = kwargs['requestType'] or ""

        arrHshPacientes = []
        for paciente in pacientes:
            hshPeciente = {}
            hshPeciente["id"] = paciente.id
            hshPeciente["dni"] = paciente.dni
            hshPeciente["nombre"] = paciente.nombre
            hshPeciente["apellido"] = paciente.apellido
            hshPeciente["domicilio"] = paciente.domicilio or ""
            hshPeciente["telefono"] = paciente.telefono
            hshPeciente["nro_afiliado"] = paciente.nroAfiliado
            hshPeciente["email"] = paciente.email
            arrHshPacientes.append(hshPeciente)

        c = Context({
          'logged_user_name':self.request.session["cedir_user_name"],
          'pacientes': arrHshPacientes,
          'apellido': apellido,
          'dni': dni,
        })

        template_name = u'turnos/buscarPaciente.html'
        if requestType == u'ajax':
            template_name = u'turnos/buscarPacienteAjax.html'

        t = loader.get_template(template_name)
        return t.render(c)
