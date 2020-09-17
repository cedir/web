from django.contrib import admin
from medicamento.models import Medicamento, Movimiento


class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'tipo', 'importe', 'stock', 'codigo_osde')
    list_filter = ('tipo', )
    search_fields = ['descripcion', ]
    ordering = ('-tipo', 'descripcion',)
    readonly_fields = ('stock', )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Medicamento, MedicamentoAdmin)


class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'cantidad', 'tipo', 'descripcion', 'medicamento')
    search_fields = ['descripcion', 'fecha', 'medicamento__descripcion']
    ordering = ('-fecha', )
    list_filter = ('fecha', 'medicamento__tipo')
    readonly_fields = ('tipo', )

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Movimiento, MovimientoAdmin)

