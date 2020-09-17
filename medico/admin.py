from django.contrib import admin
from .models import Medico

class MedicoAdmin(admin.ModelAdmin):
    actions = None

    search_fields = ['apellido', 'nombre', 'matricula']
    list_display = ('apellido', 'nombre', 'telefono', 'domicilio', 'localidad', 'mail', 'matricula', 'responsabilidad_fiscal', 'clave_fiscal')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Medico, MedicoAdmin)
