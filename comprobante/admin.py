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

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(ComprobanteAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

admin.site.register(Comprobante, ComprobanteAdmin)
