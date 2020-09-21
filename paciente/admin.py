from django.contrib import admin
from paciente.models import Paciente


class PacienteAdmin(admin.ModelAdmin):
    search_fields = ['apellido', 'nombre', 'dni']
    list_display = ('nombre', 'apellido', 'telefono', 'fechaNacimiento', 'email')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Paciente, PacienteAdmin)
