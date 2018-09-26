from django.contrib import admin
from models import Medico

class MedicoAdmin(admin.ModelAdmin):
    actions = None

    search_fields = [u'apellido', u'nombre', u'matricula']
    list_display = (u'apellido', u'nombre', u'telefono', u'domicilio', u'localidad', u'mail', u'matricula', u'matricula_osde', u'responsabilidad_fiscal', u'clave_fiscal')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Medico, MedicoAdmin)
