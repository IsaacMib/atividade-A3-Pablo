from django import template
from core.utils import get_file_type, get_fontawesome_file_icon

register = template.Library()

@register.filter
def arquivo_icon(arquivo):
    file_type = get_file_type(arquivo)
    return get_fontawesome_file_icon(file_type)