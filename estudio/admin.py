from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib import admin
from .models import Estudio, Medicacion


class MedicacionInline(admin.TabularInline):
    model = Medicacion
    extra = 1


class EstudioAdmin(admin.ModelAdmin):
    actions = None
    fields = ('fecha', 'paciente', 'practica', 'medico', 'medico_solicitante', 'obra_social', 'anestesista', 'motivo', 'informe', 'public_id', 'enlace_video', 'sucursal')
    search_fields = ['paciente__apellido', 'paciente__dni', 'fecha', ]
    list_display = ('fecha', 'paciente', 'practica', 'medico', 'obra_social', 'sucursal')
    raw_id_fields = ('paciente', )
    ordering = ('-fecha', 'paciente__apellido')
    list_filter = ('fecha',)
    readonly_fields = ('public_id', )
    #inlines = (MedicacionInline,)  # permite modificar la medicacion en crear/editar estudio

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        estudio = Estudio.objects.get(pk=object_id)
        groups = request.user.groups.filter(Q(name__icontains='Medicos') | Q(name__icontains='Tecnicos'))
        if estudio.fecha != datetime.now().date() and groups.exists():
            # dejamos a Medicos modificar el estudio solo el dia del estudio
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False

        return super(EstudioAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

    class Media:
        js = ('js/admin/estudio.js',)
        css = {'all': ('css/admin/estudio.css', )}

admin.site.register(Estudio, EstudioAdmin)

