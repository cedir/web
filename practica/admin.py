from django.contrib import admin
from models import Practica


class PracticaAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'descripcion', u'codigoMedico', u'abreviatura')
    search_fields = [u'descripcion', u'abreviatura']
    list_display = (u'id', u'descripcion', u'codigoMedico', u'abreviatura')
    ordering = (u'descripcion', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Practica, PracticaAdmin)
