from django.contrib import admin
from turno.models import InfoTurno, PeriodosNoAtencion


class InfoTurnoAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'medico__nombre', u'texto']
    list_display = (u'medico', u'texto', u'get_obras_sociales_as_string', u'get_practicas_as_string')
    ordering = (u'medico__apellido', u'medico__nombre', )
    filter_horizontal = ('practicas', u'obra_sociales')

class PeriodosNoAtencionAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'medico__nombre']
    list_display = [u'medico', u'fecha_inicio', u'fecha_fin']

admin.site.register(InfoTurno, InfoTurnoAdmin)
admin.site.register(PeriodosNoAtencion, PeriodosNoAtencionAdmin)

