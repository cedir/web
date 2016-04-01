from django.contrib import admin
from contenidos.models import *

class CategoriaAdmin(admin.ModelAdmin):
    list_display=('name', 'description')
    search_fields = ['name']
admin.site.register(Categoria, CategoriaAdmin)

class ContenidoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'createdDate', 'publishContent' )
    list_filter = ['publishContent']
    search_fields = ['title', 'description']
    filter_horizontal = ('categoria',)
admin.site.register(Contenido, ContenidoAdmin)
