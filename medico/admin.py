from django.contrib import admin
from models import Medico

class MedicoAdmin(admin.ModelAdmin):
    actions = None

    search_fields = [u'apellido', u'nombre', u'matricula']
    list_display = (u'apellido', u'nombre', u'telefono', u'domicilio', u'localidad', u'mail', u'matricula', u'responsabilidad_fiscal', u'clave_fiscal', u'facturar_amr_en_nombre_de_medico', u'facturar_osde_en_nombre_de_medico')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Medico, MedicoAdmin)
