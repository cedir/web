from django.contrib import admin
from medicamento.models import Medicamento, Movimiento


class MedicamentoAdmin(admin.ModelAdmin):
    list_display = (u'descripcion', u'tipo', u'importe', u'stock', u'codigo_osde')
    ordering = (u'tipo', u'descripcion',)


admin.site.register(Medicamento, MedicamentoAdmin)


class MovimientoAdmin(admin.ModelAdmin):
    list_display = (u'fecha', u'hora', u'cantidad', u'descripcion', u'medicamento')
    ordering = (u'-fecha', )

admin.site.register(Movimiento, MovimientoAdmin)
