from django import template

register = template.Library()

@register.simple_tag
def get_avisos_index_url():
    from avisos.models import AvisosIndexPage

    try:
        index_page = AvisosIndexPage.objects.live().first()
        if index_page:
            return index_page.url
    except Exception:
        pass
    return None


@register.inclusion_tag('include/ultimos-avisos.html', takes_context=True)
def ultimos_avisos(context, quantidade=6, titulo="Últimos Avisos", mostrar_ver_todos=True,
                   url_ver_todos=None, classe_bg="", categoria=None):
    from avisos.models import AvisosPage

    avisos_queryset = AvisosPage.objects.live().order_by('-data_publicacao')

    if categoria:
        avisos_queryset = avisos_queryset.filter(tags__name__icontains=categoria)

    avisos_list = avisos_queryset[:quantidade]

    if not url_ver_todos and mostrar_ver_todos:
        url_ver_todos = get_avisos_index_url()

    return {
        'ultimos_avisos': avisos_list,
        'titulo': titulo,
        'mostrar_ver_todos': mostrar_ver_todos,
        'url_ver_todos': url_ver_todos,
        'classe_bg': classe_bg,
        'request': context.get('request'),
    }


@register.simple_tag
def get_ultimos_avisos(quantidade=6, categoria=None):
    from avisos.models import AvisosPage

    avisos_queryset = AvisosPage.objects.live().order_by('-data_publicacao')

    if categoria:
        avisos_queryset = avisos_queryset.filter(tags__name__icontains=categoria)

    return avisos_queryset[:quantidade]
