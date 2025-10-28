from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from core.models import PageSitePadrao
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page
from noticias.models import NoticiasPage  # ajuste conforme o nome do seu app/modelo
from plone_migration.models import PloneImportedFile, PloneImportedImage
from django.db import models
from django.db.models import Q

def get_result_type(result):
    return result.content_type.model.replace('_', ' ').title()

def formatar_wagtail_types(wagtail_types):
    tipos_conhecidos = {
        "noticiaspage": "Notícias",
        "avisospage": "Avisos",
        "document": "Arquivo",
        "image": "Imagem",
        # Adicione outros tipos conhecidos aqui se desejar
    }
    return [
        {
            "titulo": tipos_conhecidos[nome],
            "filtro": nome
        }
        for nome in wagtail_types if nome in tipos_conhecidos
    ]

def search(request):
    # Redirecionamento para padronizar parâmetros (q -> query)
    if 'q' in request.GET and 'query' not in request.GET:
        params = request.GET.copy()
        params['query'] = params.pop('q')[0]  # Move o parâmetro 'q' para 'query'
        return redirect(f"{request.path}?{params.urlencode()}")

    # Obter parâmetros da requisição
    search_query = request.GET.get("query", "")
    page = request.GET.get("page", 1)
    selected_types = request.GET.getlist("type")
    date_filter = request.GET.get("date", "sempre")

    # Converter para lista de tipos (remover 'all' se outros tipos estiverem selecionados)
    if "all" in selected_types:
         selected_types = [] 
    elif not selected_types:
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
        # Dividir a query em palavras para busca mais flexível
        search_terms = search_query.strip().split()
        
        # Busca nas páginas com múltiplos termos
        pages_query = Page.objects.live().public()
        for term in search_terms:
            pages_query = pages_query.filter(
                Q(title__icontains=term) |
                Q(search_description__icontains=term)
            )
        search_results = list(pages_query)
        
        # Se não encontrou resultados com todos os termos, tenta com busca individual
        if not search_results:
            search_results = list(Page.objects.live().public().search(search_query))
        
        # Aplicar filtros de tipo
        if selected_types:
            search_results = [r for r in search_results if r.content_type.model in selected_types]
        
        # Aplicar filtro de data
        if date_cutoff:
            search_results = [
                r for r in search_results 
                if r.last_published_at and r.last_published_at >= date_cutoff
            ]
        
        # Buscar nos títulos dos arquivos com busca parcial
        arquivos_resultados = []
        if not selected_types or "document" in selected_types:
            try:
                arquivo_query = PloneImportedFile.objects.all()
                for term in search_terms:
                    arquivo_query = arquivo_query.filter(
                        Q(title__icontains=term) |
                        Q(file__icontains=term)
                    )
                arquivos_resultados = list(arquivo_query)
            except Exception as e:
                # Se houver erro com PloneImportedFile, continua sem incluir arquivos
                arquivos_resultados = []
        
        # Buscar nos títulos das imagens com busca parcial
        imagens_resultados = []
        if not selected_types or "image" in selected_types:
            try:
                imagem_query = PloneImportedImage.objects.all()
                for term in search_terms:
                    imagem_query = imagem_query.filter(
                        Q(title__icontains=term)
                    )
                imagens_resultados = list(imagem_query)
            except Exception as e:
                # Se houver erro com PloneImportedImage, continua sem incluir imagens
                imagens_resultados = []

        # Junta todos os resultados em uma única lista
        all_results = search_results + arquivos_resultados + imagens_resultados

        # Paginação dos resultados combinados
        paginator = Paginator(all_results, 10)
        try:
            paginated_results = paginator.page(page)
        except PageNotAnInteger:
            paginated_results = paginator.page(1)
        except EmptyPage:
            paginated_results = paginator.page(paginator.num_pages)

        # Registrar a query para search promotions
        Query.get(search_query).add_hit()
    else:
        paginated_results = []
    
    # Obter todos os tipos de dados presentes no Wagtail (modelos de página)
    # Buscar subclasses de Page ao invés de PageSitePadrao
    wagtail_types = list(
        ContentType.objects.filter(
            app_label__in=['noticias', 'avisos', 'eventos', 'agenda', 'editais', 'lgpd', 'paginas', 'institucional', 'home']
        ).values_list('model', flat=True)
    )

    # Adiciona os tipos primitivos do Wagtail manualmente, se não estiverem presentes
    if "document" not in wagtail_types:
        wagtail_types.append("document")
    if "image" not in wagtail_types:
        wagtail_types.append("image")

    tipos_formatados = formatar_wagtail_types(wagtail_types)

    # Montar query_params sem parâmetros de paginação
    query_params_dict = request.GET.copy()
    query_params_dict.pop('page', None)
    query_params = query_params_dict.urlencode()

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": paginated_results,
            "selected_types": selected_types,
            "selected_date": date_filter,
            "breadcrumbs": True,
            "query_params": query_params,  # agora sem paginação
            "get_result_type": get_result_type,
            "wagtail_types": tipos_formatados,
        },
    )