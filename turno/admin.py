from django.contrib import admin
from turno.models import InfoTurno


class InfoTurnoAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'medico__nombre', u'obra_social__nombre', ]
    list_display = (u'medico', u'obra_social', u'texto', )
    filter_horizontal = ('practicas',)

admin.site.register(InfoTurno, InfoTurnoAdmin)

