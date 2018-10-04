#-*- coding: utf-8 -*-
from django.contrib import admin
from models import Practica


class PracticaAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'descripcion', u'abreviatura', u'codigoMedico', u'codigo_medico_osde')
    search_fields = [u'descripcion', u'abreviatura']
    list_display = (u'descripcion', u'codigoMedico', u'codigo_medico_osde')
    ordering = (u'descripcion', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Practica, PracticaAdmin)
