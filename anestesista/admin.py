from django.contrib import admin
from .models import Anestesista, ComplejidadEstudio, Complejidad


class AnestesistaAdmin(admin.ModelAdmin):
    fields = ('nombre', 'apellido', 'matricula', 'direccion', 'localidad', 'telefono', 'email', 'porcentaje_anestesista')
    search_fields = ['nombre', 'apellido', ]
    list_display = ('apellido', 'nombre', 'matricula', 'localidad', 'telefono')
    ordering = ('apellido', 'nombre', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Anestesista, AnestesistaAdmin)


class ComplejidadEstudioAdmin(admin.ModelAdmin):
    fields = ('estudios', 'formula')
    list_display = ('practicas', 'estudios', 'formula')

admin.site.register(ComplejidadEstudio, ComplejidadEstudioAdmin)


class ComplejidadAdmin(admin.ModelAdmin):
    fields = ('importe', )
    list_display = ('id', 'importe')

admin.site.register(Complejidad, ComplejidadAdmin)

