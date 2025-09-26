from django import template
from django.template.loader import render_to_string
from noticias.models import NoticiasPage, NoticiasIndexPages

register = template.Library()


@register.inclusion_tag('include/ultimas-noticias.html', takes_context=True)
def ultimas_noticias(context, quantidade=6, titulo="Últimas Notícias", mostrar_ver_todos=True, 
                      url_ver_todos=None, classe_bg="", categoria=None):
    """
    Template tag para incluir as últimas notícias em qualquer template.
    
    Parâmetros:
    - quantidade: número de notícias a serem exibidas (padrão: 6)
    - titulo: título da seção (padrão: "Últimas Notícias")
    - mostrar_ver_todos: se deve mostrar o botão "Ver todos" (padrão: True)
    - url_ver_todos: URL para o botão "Ver todos" (opcional)
    - classe_bg: classe CSS para background (ex: "tw:bg-neutral-100")
    - categoria: filtro por categoria/tag (opcional)
    
    Exemplo de uso:
    {% load noticias_tags %}
    {% ultimas_noticias quantidade=4 titulo="Notícias Recentes" %}
    """
    
    # Busca as últimas notícias
    noticias_queryset = NoticiasPage.objects.live().order_by('-data_publicacao')
    
    # Aplica filtro de categoria se fornecido
    if categoria:
        noticias_queryset = noticias_queryset.filter(tags__name__icontains=categoria)
    
    # Limita a quantidade
    noticias_list = noticias_queryset[:quantidade]
    
    # Se url_ver_todos não foi fornecida, usa a função para buscar automaticamente
    if not url_ver_todos and mostrar_ver_todos:
        url_ver_todos = get_noticias_index_url()
    
    return {
        'ultimas_noticias': noticias_list,
        'titulo': titulo,
        'mostrar_ver_todos': mostrar_ver_todos,
        'url_ver_todos': url_ver_todos,
        'classe_bg': classe_bg,
        'request': context.get('request'),
    }


@register.simple_tag
def get_ultimas_noticias(quantidade=6, categoria=None):
    """
    Tag simples que retorna apenas o QuerySet das últimas notícias.
    
    Exemplo de uso:
    {% load noticias_tags %}
    {% get_ultimas_noticias quantidade=4 as noticias_recentes %}
    {% for noticia in noticias_recentes %}
        {{ noticia.title }}
    {% endfor %}
    """
    noticias_queryset = NoticiasPage.objects.live().order_by('-data_publicacao')
    
    if categoria:
        noticias_queryset = noticias_queryset.filter(tags__name__icontains=categoria)
    
    return noticias_queryset[:quantidade]


@register.simple_tag
def get_noticias_index_url():
    """
    Retorna a URL da primeira página do tipo NoticiasIndexPages que estiver live.
    
    Exemplo de uso:
    {% load noticias_tags %}
    {% get_noticias_index_url as url_noticias %}
    <a href="{{ url_noticias }}">Ver todas as notícias</a>
    """
    try:
        index_page = NoticiasIndexPages.objects.live().first()
        if index_page:
            return index_page.url
    except:
        pass
    return None
