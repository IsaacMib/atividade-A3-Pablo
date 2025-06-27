from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from wagtail.models import Page
from wagtail.contrib.search_promotions.models import Query

def search(request):
    # Obter parâmetros da requisição
    search_query = request.GET.get("query", "")
    page = request.GET.get("page", 1)
    selected_types = request.GET.getlist("type")  # Para múltiplos checkboxes
    date_filter = request.GET.get("date", "sempre")

    # Converter para lista de tipos (remover 'all' se outros tipos estiverem selecionados)
    if "all" in selected_types and len(selected_types) > 1:
        selected_types.remove("all")
    elif not selected_types or "all" in selected_types:
        selected_types = []  # Mostrar todos os tipos

    # Definir filtros de data
    now = timezone.now()
    date_filters = {
        'ontem': now - timedelta(days=1),
        'semana': now - timedelta(weeks=1),
        'mes': now - timedelta(days=30),
        'sempre': None,
        'intervalo': None  # Implementar lógica específica para intervalo se necessário
    }
    date_cutoff = date_filters.get(date_filter)

    # Executar busca
    if search_query:
        # Primeiro obtemos todos os resultados da busca
        search_results = list(Page.objects.live().search(search_query))
        
        # Aplicar filtros
        filtered_results = []
        for result in search_results:
            # Filtro por tipo
            type_match = not selected_types or result.content_type.model in selected_types
            
            # Filtro por data
            date_match = not date_cutoff or (
                result.last_published_at and 
                result.last_published_at >= date_cutoff
            )
            
            if type_match and date_match:
                filtered_results.append(result)
        
        search_results = filtered_results
        
        # Registrar a query para search promotions
        Query.get(search_query).add_hit()
    else:
        search_results = []

    # Paginação
    paginator = Paginator(search_results, 10)
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
            "selected_types": selected_types,
            "selected_date": date_filter,
            "breadcrumbs": True  # Para mostrar a navegação no template
        },
    )