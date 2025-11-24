"""
Template tags para utilitários gerais.
Uso: {% load core_extras %}
"""

from django import template
from django.conf import settings

from core.models import ConfiguracaoSistema

register = template.Library()


@register.simple_tag
def settings_value(name):
    """
    Obtém valor do settings.
    Uso: {% settings_value "DEBUG" %}
    """
    return getattr(settings, name, None)


@register.simple_tag
def get_config():
    """
    Obtém configuração do sistema.
    Uso: {% get_config as config %}
    """
    return ConfiguracaoSistema.get_config()


@register.inclusion_tag('core/tags/configuracao.html')
def configuracao_sistema():
    """
    Renderiza configuração do sistema.
    Uso: {% configuracao_sistema %}
    """
    return {
        'config': ConfiguracaoSistema.get_config()
    }


@register.filter(name='abs')
def abs_filter(value):
    """
    Retorna valor absoluto.
    Uso: {{ -5|abs }}
    """
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value


@register.filter(name='percentage')
def percentage(value, total):
    """
    Calcula porcentagem.
    Uso: {{ valor|percentage:total }}
    """
    try:
        value = float(value)
        total = float(total)
        if total == 0:
            return 0
        return round((value / total) * 100, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplica dois números.
    Uso: {{ 5|multiply:10 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value


@register.filter(name='divide')
def divide(value, arg):
    """
    Divide dois números.
    Uso: {{ 100|divide:10 }}
    """
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return value


@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adiciona classe CSS a um campo de formulário.
    Uso: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={'class': css_class})


@register.simple_tag
def query_transform(request, **kwargs):
    """
    Transforma query params mantendo os existentes.
    Uso: {% query_transform request page=2 %}
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        elif key in updated:
            del updated[key]
    return updated.urlencode()
