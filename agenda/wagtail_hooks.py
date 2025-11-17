import locale
import ast

from wagtail import hooks
from agenda.models import AgendaDoDiaPage
from django.utils.text import slugify
from wagtail.admin import messages
from django.shortcuts import redirect
from django.contrib import messages as django_messages
from django.utils.html import format_html

# Configurar o locale para PT-BR
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


@hooks.register('insert_editor_js')
def editor_js():
    """Registra JavaScript customizado no editor do Wagtail."""
    return format_html(
        '<script src="{0}"></script>',
        '/static/agenda/js/admin_recorrencia.js'
    )


def _mapear_tipo_recorrencia(tipo_recorrencia, intervalo_recorrencia):
    """
    Mapeia o tipo de recorrência para texto descritivo.
    
    Args:
        tipo_recorrencia: Tipo da recorrência ('days', 'months', 'years')
        intervalo_recorrencia: Intervalo da recorrência
        
    Returns:
        tuple: (tipo_slug, tipo_recorrencia_texto)
    """
    if tipo_recorrencia == 'days' and intervalo_recorrencia == 7:
        return 'semanal', 'Semanal'
    
    mapeamento_slug = {
        'days': 'diaria',
        'months': 'mensal',  
        'years': 'anual'
    }
    
    mapeamento_texto = {
        'days': 'Diária',
        'months': 'Mensal',  
        'years': 'Anual'
    }
    
    tipo_slug = mapeamento_slug.get(tipo_recorrencia, tipo_recorrencia)
    tipo_texto = mapeamento_texto.get(tipo_recorrencia, tipo_recorrencia.title())
    
    return tipo_slug, tipo_texto


def atualizar_titulo_slug_agenda_recorrente(page, parent_page):
    """
    Atualiza o título e slug de uma agenda recorrente baseado nas configurações atuais.
    SEMPRE reconstrói do zero usando: parent_page.title + data + tipo_recorrencia.
    
    Args:
        page: Instância de AgendaDoDiaPage
        parent_page: Página pai da agenda
    """
    data_slug = page.date.strftime('%Y-%m-%d')
    data_extensa = page.date.strftime("%d de %B")
    
    tipo_slug, tipo_recorrencia_texto = _mapear_tipo_recorrencia(
        page.tipo_recorrencia, 
        page.intervalo_recorrencia
    )
    
    page.slug = slugify(f"{parent_page.slug}-agenda-recorrente-{tipo_slug}-{data_slug}")
    page.title = f"{parent_page.title} - Agenda Recorrente {tipo_recorrencia_texto} - {data_extensa}"


def atualizar_titulo_slug_agenda_normal(page, parent_page):
    """
    Atualiza o título e slug de uma agenda normal (sem recorrência).
    Formato: {Nome do Pai} - Agenda do Dia - {Data}
    
    Args:
        page: Instância de AgendaDoDiaPage
        parent_page: Página pai da agenda
    """
    data_slug = page.date.strftime('%Y-%m-%d')
    data_extensa = page.date.strftime("%d de %B de %Y")
    
    page.slug = slugify(f"{parent_page.slug}-agenda-{data_slug}")
    page.title = f"{parent_page.title} - Agenda do Dia - {data_extensa}"


def atualizar_titulo_slug_agenda(page, parent_page):
    """
    Atualiza o título e slug de uma agenda (recorrente ou normal).
    Detecta automaticamente o tipo e aplica a formatação adequada.
    
    Args:
        page: Instância de AgendaDoDiaPage
        parent_page: Página pai da agenda
    """
    is_recorrente = page.habilitar_recorrencia and page.tipo_recorrencia != 'none'
    
    if is_recorrente:
        atualizar_titulo_slug_agenda_recorrente(page, parent_page)
    else:
        atualizar_titulo_slug_agenda_normal(page, parent_page)


def processar_erro_agenda(e):
    """
    Processa exceções de agendas e extrai mensagens de erro.
    
    Args:
        e: Exceção capturada
        
    Returns:
        str: Mensagem de erro formatada
    """
    error_message = str(e)
    try:
        data = ast.literal_eval(error_message)
        if 'slug' in data:
            error_message = data['slug'][0]
    except:
        pass
    
    return error_message


@hooks.register('after_create_page')
def do_after_agendadodia_page_create(request, page):
    """Hook executado após criar uma nova página de agenda."""
    if not isinstance(page, AgendaDoDiaPage):
        return
    
    parent_page = page.get_parent()
    if not parent_page:
        return
    
    # Atualizar título e slug baseado no tipo (recorrente ou normal)
    atualizar_titulo_slug_agenda(page, parent_page)
    
    # Verificar se é recorrente para mensagem de sucesso
    is_recorrente = page.habilitar_recorrencia and page.tipo_recorrencia != 'none'
    
    try:
        # Salvar as mudanças no modelo antes de criar revisão
        page.save(update_fields=['title', 'slug'])
        
        # Criar nova revisão com as alterações
        new_revision = page.save_revision()
        
        if page.live:
            # Page has been created and published at the same time,
            # so ensure that the updated title is on the published version too
            new_revision.publish()
        
        # Mostrar informação sobre recorrência (apenas se for recorrente)
        if is_recorrente:
            proximas_datas = page.get_proximas_datas_recorrencia(limite=5)
            if len(proximas_datas) > 1:
                messages.success(
                    request, 
                    f"Agenda criada com sucesso! Esta agenda se repetirá em datas próximas devido à configuração de recorrência."
                )
            
    except Exception as e:
        error_message = processar_erro_agenda(e)
        
        # Remover mensagens existentes
        list(django_messages.get_messages(request))
        
        # Remover a página em caso de erro
        page.delete()
        messages.error(request, error_message)
        
        # Redirecionar para wagtailadmin_explore com parent_page_id
        return redirect("wagtailadmin_explore", parent_page_id=parent_page.id)


@hooks.register('after_publish_page')
def do_after_agendadodia_page_publish(request, page):
    """Hook executado após publicar/atualizar uma página de agenda existente."""
    if not isinstance(page, AgendaDoDiaPage):
        return
    
    parent_page = page.get_parent()
    if not parent_page:
        return
    
    # Guardar valores atuais para comparação
    titulo_antes = page.title
    slug_antes = page.slug
    
    # Atualizar título e slug (SEMPRE reconstrói baseado nas configurações)
    atualizar_titulo_slug_agenda(page, parent_page)
    
    # Só salvar se houve mudança
    if titulo_antes != page.title or slug_antes != page.slug:
        try:
            # Salvar as mudanças no modelo antes de criar revisão
            page.save(update_fields=['title', 'slug'])
            
            # Criar nova revisão com as alterações
            new_revision = page.save_revision()
            
            if page.live:
                # Ensure that the updated title is on the published version
                new_revision.publish()
                
        except Exception as e:
            error_message = processar_erro_agenda(e)
            messages.error(request, error_message)