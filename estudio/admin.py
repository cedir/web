from datetime import datetime, timedelta
from django.contrib import admin
from models import Estudio, Medicacion


class MedicacionInline(admin.TabularInline):
    model = Medicacion
    extra = 1


class EstudioAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'fecha', u'paciente', u'practica', u'medico', u'medico_solicitante', u'obra_social', u'anestesista', u'motivo', u'informe', u'public_id', u'enlace_video')
    search_fields = [u'paciente__apellido', u'paciente__dni', u'fecha', ]
    list_display = (u'fecha', u'paciente', u'practica', u'medico', u'obra_social')
    raw_id_fields = (u'paciente', )
    ordering = (u'-fecha', u'paciente__apellido')
    list_filter = (u'fecha',)
    readonly_fields = (u'public_id', )
    #inlines = (MedicacionInline,)  # permite modificar la medicacion en crear/editar estudio

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        estudio = Estudio.objects.get(pk=object_id)

        if estudio.fecha != datetime.now().date() and request.user.groups.filter(name__icontains='Medicos').exists():
            # dejamos a Medicos modificar el estudio solo el dia del estudio
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False

        return super(EstudioAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

    class Media:
        js = (u'js/admin/estudio.js',)
        css = {u'all': (u'css/admin/estudio.css', )}

admin.site.register(Estudio, EstudioAdmin)

