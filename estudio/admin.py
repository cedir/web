from django.contrib import admin
from models import Estudio

class EstudioAdmin(admin.ModelAdmin):
    actions = None
    search_fields = [u'paciente__apellido', u'fechaEstudio', ]
    list_display = (u'fechaEstudio', u'paciente', u'motivoEstudio', )
    raw_id_fields = (u'paciente', )
    ordering = (u'-fechaEstudio',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        js = ('js/admin/estudio.js',)

admin.site.register(Estudio, EstudioAdmin)

