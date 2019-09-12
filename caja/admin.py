from django.contrib import admin
from caja.models import MovimientoCaja

# Register your models here.
class MovimientoCajaAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'fecha', u'hora', u'monto', u'concepto')
    search_fields = [u'tipo', u'concepto']
    list_display = (u'fecha', u'hora', u'monto', u'concepto')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(MovimientoCajaAdmin, self).changeform_view(request, object_id, extra_context=extra_context)


admin.site.register(MovimientoCaja, MovimientoCajaAdmin)
