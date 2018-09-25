from django.contrib import admin
from models import ObraSocial

class ObraSocialAdmin(admin.ModelAdmin):
    actions = None
    search_fields = [u'nombre']
    list_display = (u'nombre', u'telefono', u'localidad', u'direccion', u'codigo_postal', u'observaciones')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(ObraSocial, ObraSocialAdmin)
