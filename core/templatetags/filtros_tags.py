from django import template

register = template.Library()


@register.inclusion_tag("tags/filtros.html", takes_context=True)
def filtros_ano_tag(context, mostrar_ano=True, mostrar_tag=True, texto_botao="Filtrar"):
    """
    Renderiza os filtros de Ano e Tag para páginas de listagem.
    
    Args:
        context: Contexto do template
        mostrar_ano: Exibir filtro de ano (padrão: True)
        mostrar_tag: Exibir filtro de tag (padrão: True)
        texto_botao: Texto do botão de filtrar (padrão: "Filtrar")
    
    O contexto deve conter:
        - anos_disponiveis: QuerySet com os anos disponíveis
        - tags: QuerySet com as tags disponíveis
        - ano: Ano atualmente selecionado (opcional)
        - tag: Tag atualmente selecionada (opcional)
    """
    return {
        'anos_disponiveis': context.get('anos_disponiveis', []),
        'tags': context.get('tags', []),
        'ano': context.get('ano'),
        'tag': context.get('tag'),
        'mostrar_ano': mostrar_ano,
        'mostrar_tag': mostrar_tag,
        'texto_botao': texto_botao,
    }
