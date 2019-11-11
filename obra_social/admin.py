from django.contrib import admin
from models import ObraSocial, ArancelObraSocial


class ObraSocialAdmin(admin.ModelAdmin):
    actions = None
    search_fields = [u'nombre']
    list_display = (u'nombre', u'telefono', u'localidad', u'direccion', u'codigo_postal', u'valor_aproximado_pension')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(ObraSocial, ObraSocialAdmin)


class ArancelObraSocialAdmin(admin.ModelAdmin):
    actions = None
    search_fields = [u'practica__descripcion', u'obra_social__nombre']
    list_display = (u'practica', u'obra_social', u'precio', u'precio_anestesia', u'fecha')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(ArancelObraSocial, ArancelObraSocialAdmin)
