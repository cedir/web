from django.contrib import admin
from comprobante.models import Comprobante


class ComprobanteAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'fecha_emision', 'nombre_cliente', 'condicion_fiscal', 'responsable', 'sub_tipo', 'numero', 'tipo_comprobante', u'total_facturado', )
    list_display = (u'fecha_emision', 'nombre_cliente', 'sub_tipo', 'numero', 'tipo_comprobante', u'total_facturado', )


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        #Return nothing to make sure user can't update any data
        pass

admin.site.register(Comprobante, ComprobanteAdmin)

