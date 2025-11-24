"""
Template tags para filtros de texto.
Uso: {% load text_filters %}
"""

from django import template
from django.utils.html import strip_tags
from django.utils.text import Truncator

from core.utils import truncar_texto, formatar_telefone, formatar_cpf, formatar_cnpj

register = template.Library()


@register.filter(name='truncate_chars')
def truncate_chars(value, arg):
    """
    Trunca texto em X caracteres.
    Uso: {{ texto|truncate_chars:100 }}
    """
    try:
        length = int(arg)
    except (ValueError, TypeError):
        return value
    
    return truncar_texto(value, length)


@register.filter(name='truncate_words')
def truncate_words(value, arg):
    """
    Trunca texto em X palavras.
    Uso: {{ texto|truncate_words:20 }}
    """
    try:
        length = int(arg)
    except (ValueError, TypeError):
        return value
    
    truncate = Truncator(value)
    return truncate.words(length, html=True)


@register.filter(name='strip_html')
def strip_html(value):
    """
    Remove tags HTML do texto.
    Uso: {{ html_text|strip_html }}
    """
    return strip_tags(value)


@register.filter(name='formatar_telefone')
def formatar_telefone_filter(value):
    """
    Formata número de telefone.
    Uso: {{ telefone|formatar_telefone }}
    """
    return formatar_telefone(value)


@register.filter(name='formatar_cpf')
def formatar_cpf_filter(value):
    """
    Formata CPF.
    Uso: {{ cpf|formatar_cpf }}
    """
    return formatar_cpf(value)


@register.filter(name='formatar_cnpj')
def formatar_cnpj_filter(value):
    """
    Formata CNPJ.
    Uso: {{ cnpj|formatar_cnpj }}
    """
    return formatar_cnpj(value)


@register.filter(name='replace')
def replace(value, args):
    """
    Substitui texto.
    Uso: {{ texto|replace:"old,new" }}
    """
    try:
        old, new = args.split(',')
        return value.replace(old, new)
    except (ValueError, AttributeError):
        return value


@register.filter(name='startswith')
def startswith(value, arg):
    """
    Verifica se string começa com determinado valor.
    Uso: {% if texto|startswith:"http" %}
    """
    try:
        return value.startswith(arg)
    except (AttributeError, TypeError):
        return False


@register.filter(name='endswith')
def endswith(value, arg):
    """
    Verifica se string termina com determinado valor.
    Uso: {% if texto|endswith:".pdf" %}
    """
    try:
        return value.endswith(arg)
    except (AttributeError, TypeError):
        return False
