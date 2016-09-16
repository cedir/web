from django.contrib import admin
from medicamento.models import Medicamento, Movimiento


class MedicamentoAdmin(admin.ModelAdmin):
    list_display = (u'descripcion', u'tipo', u'importe', u'stock', u'codigo_osde')
    list_filter = (u'tipo', )
    search_fields = [u'descripcion', ]
    ordering = (u'-tipo', u'descripcion',)
    readonly_fields = (u'stock', )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Medicamento, MedicamentoAdmin)


class MovimientoAdmin(admin.ModelAdmin):
    list_display = (u'fecha', u'hora', u'cantidad', u'tipo', u'descripcion', u'medicamento')
    search_fields = [u'descripcion', u'fecha', u'medicamento__descripcion']
    ordering = (u'-fecha', )
    list_filter = (u'fecha', u'medicamento__tipo')
    readonly_fields = (u'tipo', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Movimiento, MovimientoAdmin)

