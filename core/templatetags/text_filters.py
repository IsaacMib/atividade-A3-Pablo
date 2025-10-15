from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html

register = template.Library()


@register.filter(name='add_link_to_trimmed_text')
def add_link_to_trimmed_text(text_length, link_path):
    return mark_safe(format_html('<a href="{}">Ver mais</a>', link_path))
