from django import template

register = template.Library()

@register.filter
def result_type(result):
    """
    Retorna o tipo do objeto resultante da busca, baseado no model do content_type.
    """
    tipo = result.content_type.model
    if tipo.lower() == "noticiaspage":
        return "Notícia"
    return tipo.replace('_', ' ').title()