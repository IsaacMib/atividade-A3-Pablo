from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Page
from wagtail.contrib.search_promotions.models import Query
from home.models import HomePage  # Importe outros models conforme necessário

def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)
    content_type = request.GET.get("type", None)  # Novo parâmetro para filtrar por tipo

    # Search
    if search_query:
        # Pesquisa em todas as páginas publicadas
        search_results = Page.objects.live().search(search_query)
        
        # Registrar a query para search promotions
        query = Query.get(search_query)
        query.add_hit()
        
        # Filtrar por tipo de conteúdo se especificado
        if content_type:
            if content_type == 'home':
                search_results = search_results.type(HomePage)
            # Adicione outros tipos conforme necessário
            
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 12)  # 12 itens por página
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "content_type": content_type,
        },
    )