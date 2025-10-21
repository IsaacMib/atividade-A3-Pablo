from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html

register = template.Library()


@register.filter(name='add_link_to_trimmed_text')
def add_link_to_trimmed_text(text_content, link_path):
    return mark_safe(format_html(
        '<p lang="pt-BR" class="card-linha-do-tempo__description">{}<a href="{}" class="ver-mais-link">Ver mais</a></p>',
        text_content,
        link_path
    ))
