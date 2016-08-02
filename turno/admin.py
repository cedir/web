from django.contrib import admin
from turno.models import InfoTurno


class InfoTurnoAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'medico__nombre', u'texto']
    list_display = (u'medico', u'texto', u'get_obras_sociales_as_string')
    filter_horizontal = ('practicas', u'obra_sociales')

admin.site.register(InfoTurno, InfoTurnoAdmin)

