from django import template

register = template.Library()


@register.filter
def belong_to_category(contenido, category_name):
    """
    Return True if contenido object belongs to category with name category_name
    """
    return contenido.categoria.filter(name__contains=category_name).exists()

