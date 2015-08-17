from django.contrib import admin
from medico.models import InfoMedico


class InfoMedicoAdmin(admin.ModelAdmin):
    search_fields = [u'medico__apellido', u'medico__nombre', u'obra_social__nombre', ]
    list_display = (u'medico', u'obra_social', u'texto', )

admin.site.register(InfoMedico, InfoMedicoAdmin)
