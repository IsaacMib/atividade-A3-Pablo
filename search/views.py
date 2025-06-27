from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from wagtail.models import Page
from wagtail.contrib.search_promotions.models import Query

def search(request):
    # Redirecionamento para padronizar parâmetros (q -> query)
    if 'q' in request.GET and 'query' not in request.GET:
        params = request.GET.copy()
        params['query'] = params.pop('q')[0]  # Move o parâmetro 'q' para 'query'
        return redirect(f"{request.path}?{params.urlencode()}")
    
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
        search_results = Page.objects.live().search(search_query)
        
        # Aplicar filtros de tipo
        if selected_types:
            search_results = [r for r in search_results if r.content_type.model in selected_types]
        
        # Converter para lista para filtro de data
        search_results = list(search_results)
        
        # Aplicar filtro de data
        if date_cutoff:
            search_results = [
                r for r in search_results 
                if r.last_published_at and r.last_published_at >= date_cutoff
            ]
        
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
            "breadcrumbs": True,
            # Adiciona todos os parâmetros para manter os filtros
            "query_params": request.GET.urlencode()
        },
    )