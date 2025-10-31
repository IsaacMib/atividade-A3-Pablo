from django import template
from django.utils.html import format_html
from wagtail.models import Site
from core.models import SiteSettings
from urllib.parse import quote

register = template.Library()


@register.inclusion_tag("tags/compartilhamento.html", takes_context=True)
def compartilhamento_social(context, page=None, titulo=None, descricao=None):
    """
    Renderiza os botões de compartilhamento nas redes sociais.
    
    Args:
        context: Contexto do template
        page: Página atual (opcional, será inferida do contexto se não fornecida)
        titulo: Título customizado para compartilhamento (opcional)
        descricao: Descrição customizada para compartilhamento (opcional)
    """
    request = context.get('request')
    if not request:
        return {'redes_compartilhamento': []}
    
    # Obtém a página atual se não foi fornecida
    if not page:
        page = context.get('page') or context.get('self')
    
    # Obtém as configurações do site
    site = Site.find_for_request(request)
    site_settings = SiteSettings.for_site(site)
    
    # Se o compartilhamento não está habilitado, retorna vazio
    if not site_settings.tem_compartilhamento_habilitado():
        return {'redes_compartilhamento': []}
    
    # Obtém as redes habilitadas
    redes_habilitadas = site_settings.get_redes_sociais_compartilhamento()
    
    # Prepara os dados para compartilhamento
    url_atual = request.build_absolute_uri()
    
    # Define título e descrição
    if not titulo and page:
        titulo = getattr(page, 'title', 'Página')
    if not descricao and page:
        descricao = getattr(page, 'descricao', '') or getattr(page, 'search_description', '')
    
    titulo_encoded = quote(titulo or 'Confira esta página')
    descricao_encoded = quote(descricao or '')
    url_encoded = quote(url_atual)
    
    # Monta as URLs de compartilhamento
    redes_compartilhamento = []
    for rede in redes_habilitadas:
        rede_info = rede.copy()
        
        if rede['codigo'] == 'facebook':
            rede_info['url'] = f"https://www.facebook.com/sharer/sharer.php?u={url_encoded}"
            
        elif rede['codigo'] == 'twitter':
            rede_info['url'] = f"https://twitter.com/intent/tweet?text={titulo_encoded}&url={url_encoded}"
            
        elif rede['codigo'] == 'linkedin':
            rede_info['url'] = f"https://www.linkedin.com/sharing/share-offsite/?url={url_encoded}"
            
        elif rede['codigo'] == 'whatsapp':
            texto = f"{titulo or ''} {url_atual}"
            rede_info['url'] = f"https://wa.me/?text={quote(texto)}"
            
        elif rede['codigo'] == 'telegram':
            rede_info['url'] = f"https://t.me/share/url?url={url_encoded}&text={titulo_encoded}"
            
        elif rede['codigo'] == 'email':
            subject = quote(f"Compartilhando: {titulo or 'Página interessante'}")
            body = quote(f"Olá!\n\nGostaria de compartilhar esta página com você:\n\n{titulo or 'Página'}\n{url_atual}\n\n{descricao or ''}")
            rede_info['url'] = f"mailto:?subject={subject}&body={body}"
            
        elif rede['codigo'] == 'copy':
            rede_info['url'] = url_atual
            rede_info['copy_link'] = True
            
        redes_compartilhamento.append(rede_info)
    
    return {
        'redes_compartilhamento': redes_compartilhamento,
        'url_atual': url_atual,
        'titulo': titulo,
        'descricao': descricao,
    }


@register.simple_tag(takes_context=True)
def url_compartilhamento(context, rede, page=None, titulo=None):
    """
    Retorna a URL de compartilhamento para uma rede específica.
    
    Args:
        context: Contexto do template
        rede: Código da rede social ('facebook', 'twitter', etc.)
        page: Página atual (opcional)
        titulo: Título customizado (opcional)
    """
    request = context.get('request')
    if not request:
        return ''
    
    # Obtém a página atual se não foi fornecida
    if not page:
        page = context.get('page') or context.get('self')
    
    url_atual = request.build_absolute_uri()
    
    # Define título
    if not titulo and page:
        titulo = getattr(page, 'title', 'Página')
    
    titulo_encoded = quote(titulo or 'Confira esta página')
    url_encoded = quote(url_atual)
    
    # Retorna a URL de acordo com a rede
    if rede == 'facebook':
        return f"https://www.facebook.com/sharer/sharer.php?u={url_encoded}"
    elif rede == 'twitter':
        return f"https://twitter.com/intent/tweet?text={titulo_encoded}&url={url_encoded}"
    elif rede == 'linkedin':
        return f"https://www.linkedin.com/sharing/share-offsite/?url={url_encoded}"
    elif rede == 'whatsapp':
        texto = f"{titulo or ''} {url_atual}"
        return f"https://wa.me/?text={quote(texto)}"
    elif rede == 'telegram':
        return f"https://t.me/share/url?url={url_encoded}&text={titulo_encoded}"
    elif rede == 'email':
        subject = quote(f"Compartilhando: {titulo or 'Página interessante'}")
        body = quote(f"Olá!\n\nGostaria de compartilhar esta página com você:\n\n{titulo or 'Página'}\n{url_atual}")
        return f"mailto:?subject={subject}&body={body}"
    
    return ''