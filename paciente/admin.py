from django.contrib import admin
from paciente.models import Paciente


class PacienteAdmin(admin.ModelAdmin):
    search_fields = [u'apellido', u'nombre', 'dni']
    list_display = (u'nombre', u'apellido', u'telefono', u'fechaNacimiento', u'email')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Paciente, PacienteAdmin)

