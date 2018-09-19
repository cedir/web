from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def to_aaaa_mm_dd(value):
    """
    Cambiar formato desde dd/mm/aaaa a aaaa-mm-dd
    :param value:
    :return:
    """
    dia, mes, anio = value.strip().split('/')
    return '{}-{}-{}'.format(anio, mes, dia)
