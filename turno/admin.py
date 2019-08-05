from django.contrib import admin
from turno.models import InfoTurno, PeriodoSinAtencion, Turno


class TurnoAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'paciente__apellido', u'fechaTurno']
    list_display = (u'fechaTurno', u'horaInicio', u'paciente', u'medico', u'obraSocial',)
    ordering = (u'-fechaTurno', u'-horaInicio', )
    raw_id_fields = (u'paciente', )
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
    search_fields = [u'medico__apellido', u'medico__nombre', u'texto']
    list_display = (u'medico', u'texto', u'get_obras_sociales_as_string', u'get_practicas_as_string')
    ordering = (u'medico__apellido', u'medico__nombre', )
    filter_horizontal = ('practicas', u'obra_sociales')


class PeriodoSinAtencionAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'medico__nombre']
    list_display = [u'medico', u'fecha_inicio', u'fecha_fin']
    ordering = (u'medico__apellido', u'fecha_inicio', )


admin.site.register(Turno, TurnoAdmin)
admin.site.register(InfoTurno, InfoTurnoAdmin)
admin.site.register(PeriodoSinAtencion, PeriodoSinAtencionAdmin)
