from django.contrib import admin
from turno.models import InfoTurno, PeriodoSinAtencion, Turno


class TurnoAdmin(admin.ModelAdmin):
    search_fields = ['medico__apellido', 'paciente__apellido', 'fechaTurno']
    list_display = ('fechaTurno', 'horaInicio', 'paciente', 'medico', 'obraSocial',)
    ordering = ('-fechaTurno', '-horaInicio', )
    raw_id_fields = ('paciente', )
    filter_horizontal = ('practicas',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(TurnoAdmin, self).changeform_view(request, object_id, extra_context=extra_context)


class InfoTurnoAdmin(admin.ModelAdmin):
    search_fields = ['medico__apellido', 'medico__nombre', 'texto']
    list_display = ('medico', 'texto', 'get_obras_sociales_as_string', 'get_practicas_as_string')
    ordering = ('medico__apellido', 'medico__nombre', )
    filter_horizontal = ('practicas', 'obra_sociales')


class PeriodoSinAtencionAdmin(admin.ModelAdmin):
    search_fields = ['medico__apellido', 'medico__nombre']
    list_display = ['medico', 'fecha_inicio', 'fecha_fin']
    ordering = ('medico__apellido', 'fecha_inicio', )


admin.site.register(Turno, TurnoAdmin)
admin.site.register(InfoTurno, InfoTurnoAdmin)
admin.site.register(PeriodoSinAtencion, PeriodoSinAtencionAdmin)
