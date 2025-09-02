from django import template
from blocks.utils import get_color_by_class_titulo_bg

register = template.Library()

@register.filter
def bgcolor_from_class(bgclass):
    return get_color_by_class_titulo_bg(bgclass)
