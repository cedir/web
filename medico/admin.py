from django.contrib import admin
from models import Anestesista


class AnestesistaAdmin(admin.ModelAdmin):
    fields = (u'nombre', u'apellido', u'matricula', u'direccion', u'localidad', u'telefono', u'email')
    search_fields = [u'nombre', u'apellido', ]
    list_display = (u'apellido', u'nombre', u'matricula', u'localidad', u'telefono')
    ordering = (u'apellido', u'nombre', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Anestesista, AnestesistaAdmin)

