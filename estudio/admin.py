from django.contrib import admin
from models import Estudio


class EstudioAdmin(admin.ModelAdmin):
    actions = None
    fields = (u'fechaEstudio', u'paciente', u'practica', u'medico', u'medicoSolicitante', u'obraSocial', u'anestesista', u'motivoEstudio', u'informe', u'public_id', u'enlace_video')
    search_fields = [u'paciente__apellido', u'fechaEstudio', ]
    list_display = (u'fechaEstudio', u'paciente', u'practica', u'medico', u'obraSocial')
    raw_id_fields = (u'paciente', )
    ordering = (u'-fechaEstudio',)
    list_filter = (u'fechaEstudio',)
    readonly_fields = (u'public_id', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        js = (u'js/admin/estudio.js',)
        css = {u'all': (u'css/admin/estudio.css', )}

admin.site.register(Estudio, EstudioAdmin)

