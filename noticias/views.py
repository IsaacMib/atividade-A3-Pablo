import requests
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.panels import FieldPanel

from .models import NoticiasPage, NoticiaRemota, NoticiasIndexPages
from core.models import ApiSettings
from wagtail.models import Site

class NoticiasPageViewSet(ModelViewSet):
    model = NoticiasPage
    ordering = ("title",)
    list_display = ("title", "url", "destaque",)
    search_fields = ("title","destaque",)
    icon = "document"
    inspect_view_enabled = True


def noticia_remota_detail_view(request, noticia_id):
    """
    View para buscar e renderizar uma notícia de um portal externo.
    """
    try:
        site = Site.objects.get(is_default_site=True)
        api_settings = ApiSettings.for_site(site)
    except (Site.DoesNotExist, ApiSettings.DoesNotExist):
        raise Http404("Configurações da API não encontradas.")

    if not api_settings.api_habilitada:
        raise Http404("Integração com API externa não está habilitada.")

    # 1. Obter token de autenticação
    token_url = f"{api_settings.api_url.rstrip('/')}/api/v1/get-token/"
    try:
        response = requests.post(
            token_url,
            data={'username': api_settings.api_usuario, 'password': api_settings.api_senha},
            timeout=10
        )
        response.raise_for_status()
        token = response.json().get('token')
        if not token:
            raise Http404("Falha ao obter token de autenticação.")
    except requests.RequestException:
        raise Http404("Não foi possível conectar à API para obter o token.")

    # 2. Buscar os dados da notícia específica
    noticia_url = f"{api_settings.api_url.rstrip('/')}/api/v1/shared-content/noticia/{noticia_id}/"
    headers = {'Authorization': f"Token {token}"}
    try:
        response = requests.get(noticia_url, headers=headers, timeout=15)
        if response.status_code == 404:
            raise Http404("Notícia remota não encontrada.")
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        raise Http404("Não foi possível buscar os dados da notícia remota.")

    # 3. Criar um objeto NoticiaRemota e renderizar o template
    noticia_remota = NoticiaRemota(data, api_base_url=api_settings.api_url)
    
    # Reutilizamos o template da notícia local
    # Buscamos a página de índice de notícias para usar no contexto (breadcrumbs, etc.)
    noticias_index = NoticiasIndexPages.objects.live().first()

    return render(request, 'noticias/noticias_page.html', {
        'page': noticia_remota,
        'self': noticias_index, # 'self' é usado nos templates do Wagtail para a página de índice
        'ultimas_noticias': noticias_index.get_ultimas_noticias() if noticias_index else []
    })
