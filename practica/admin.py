#-*- coding: utf-8 -*-
from django.contrib import admin
from .models import Practica


class PracticaAdmin(admin.ModelAdmin):
    actions = None
    fields = ('descripcion', 'abreviatura', 'codigoMedico', 'codigo_medico_osde')
    search_fields = ['descripcion', 'abreviatura']
    list_display = ('descripcion', 'codigoMedico', 'codigo_medico_osde')
    ordering = ('descripcion', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Practica, PracticaAdmin)
