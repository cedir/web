from django.contrib import admin
from models import Anestesista, ComplejidadEstudio, Complejidad


class AnestesistaAdmin(admin.ModelAdmin):
    fields = (u'nombre', u'apellido', u'matricula', u'direccion', u'localidad', u'telefono', u'email', u'porcentaje_anestesista')
    search_fields = [u'nombre', u'apellido', ]
    list_display = (u'apellido', u'nombre', u'matricula', u'localidad', u'telefono')
    ordering = (u'apellido', u'nombre', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Anestesista, AnestesistaAdmin)


class ComplejidadEstudioAdmin(admin.ModelAdmin):
    fields = (u'estudios', 'formula')
    list_display = (u'practicas', u'estudios', 'formula')

admin.site.register(ComplejidadEstudio, ComplejidadEstudioAdmin)


class ComplejidadAdmin(admin.ModelAdmin):
    fields = (u'importe', )
    list_display = (u'id', 'importe')

admin.site.register(Complejidad, ComplejidadAdmin)

