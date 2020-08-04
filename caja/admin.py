from django.contrib import admin
from caja.models import MovimientoCaja

# Register your models here.
class MovimientoCajaAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'fecha', u'hora', u'monto', u'concepto', u'estudio', u'tipo', u'medico', u'estado')
    search_fields = [u'tipo', u'concepto']
    list_display = (u'fecha', u'hora', u'monto', u'monto_acumulado', u'concepto', u'estudio')
    raw_id_fields = (u'estudio', )

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            if obj.monto == None:
                obj.monto = 0
            obj.monto_acumulado = obj.monto + MovimientoCaja.objects.last().monto_acumulado
        super(MovimientoCajaAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj:
            readonly_fields = list(self.fields)
        return readonly_fields

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
        return super(MovimientoCajaAdmin, self).changeform_view(request, object_id, extra_context=extra_context)


admin.site.register(MovimientoCaja, MovimientoCajaAdmin)
