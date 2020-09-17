from django.contrib import admin
from contenidos.models import Contenido, Categoria

class CategoriaAdmin(admin.ModelAdmin):
    list_display=('name', 'description')
    search_fields = ['name']


admin.site.register(Categoria, CategoriaAdmin)


class CategoriaFilter(admin.SimpleListFilter):
    title = 'Categorias'
    parameter_name = 'categoria'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Categoria.objects.all().order_by('name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(categoria__id=self.value())
        else:
            return queryset


class ContenidoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'createdDate', 'publishContent' )
    list_filter = ('publishContent', CategoriaFilter, )
    search_fields = ['title', 'description']
    filter_horizontal = ('categoria',)


admin.site.register(Contenido, ContenidoAdmin)

