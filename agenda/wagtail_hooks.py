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


def atualizar_titulo_slug_agenda_recorrente(page, parent_page, is_new=False):
    """
    Atualiza o título e slug de uma agenda recorrente.
    
    Args:
        page: Instância de AgendaDoDiaPage
        parent_page: Página pai da agenda
        is_new: Se True, é uma nova página. Se False, é uma atualização.
    
    Returns:
        tuple: (titulo_original, slug_original) extraídos da página
    """
    # Guardar o título e slug originais da agenda
    titulo_original = page.title
    slug_original = page.slug
    
    # Se não é nova página, remover sufixos de recorrência antigos do título
    if not is_new:
        for sufixo in [' - Agenda Recorrente Diária', ' - Agenda Recorrente Semanal', 
                      ' - Agenda Recorrente Mensal', ' - Agenda Recorrente Anual']:
            if sufixo in titulo_original:
                titulo_original = titulo_original.replace(sufixo, '').strip()
                # Remove também o título do pai se estiver no início
                if titulo_original.startswith(f"{parent_page.title} - "):
                    titulo_original = titulo_original.replace(f"{parent_page.title} - ", '', 1).strip()
                break
    
    # Atualizar o slug para incluir "recorrente" e a data
    data_slug = page.date.strftime('%Y-%m-%d')
    
    # Mapear tipos de recorrência para texto descritivo no slug
    if page.tipo_recorrencia == 'days' and page.intervalo_recorrencia == 7:
        tipo_slug = 'semanal'
    else:
        tipo_slug = {
            'days': 'diaria',
            'months': 'mensal',  
            'years': 'anual'
        }.get(page.tipo_recorrencia, page.tipo_recorrencia)
    
    if "recorrente" not in slug_original:
        page.slug = slugify(f"{slug_original}-recorrente-{tipo_slug}-{data_slug}")
    else:
        # Se já tem recorrente, atualiza tipo e data
        page.slug = slugify(f"{slug_original}-{tipo_slug}-{data_slug}")

    # Mapear tipos de recorrência para texto descritivo no título
    if page.tipo_recorrencia == 'days' and page.intervalo_recorrencia == 7:
        tipo_recorrencia_texto = 'Semanal'
    else:
        tipo_recorrencia_texto = {
            'days': 'Diária',
            'months': 'Mensal',  
            'years': 'Anual'
        }.get(page.tipo_recorrencia, page.tipo_recorrencia.title())
    
    # Atualizar o título para incluir o título do pai, título original, tipo de recorrência e data
    data_extensa = page.date.strftime("%d de %B")
    page.title = f"{parent_page.title} - {titulo_original} - Agenda Recorrente {tipo_recorrencia_texto} - {data_extensa}"
    
    return titulo_original, slug_original


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
        pass  # Se não conseguir fazer parse, usa a mensagem original
    
    return error_message


@hooks.register('after_create_page')
def do_after_agendadodia_page_create(request, page):
    """Hook executado após criar uma nova página de agenda."""
    if isinstance(page, AgendaDoDiaPage):
        parent_page = page.get_parent()
        if parent_page:
            # Verificar se já foi processado para evitar duplicação
            if parent_page.title in page.slug and ("recorrente" in page.slug or page.date.strftime('%Y-%m-%d') in page.slug):
                return
            
            # Processar apenas agendas recorrentes
            if page.habilitar_recorrencia and page.tipo_recorrencia != 'none':
                # Atualizar título e slug para agenda recorrente
                atualizar_titulo_slug_agenda_recorrente(page, parent_page, is_new=True)
            
                try:
                    new_revision = page.save_revision()
                    if page.live:
                        # page has been created and published at the same time,
                        # so ensure that the updated title is on the published version too
                        new_revision.publish()
                        
                    # Mostrar informação sobre recorrência
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
    if isinstance(page, AgendaDoDiaPage):
        parent_page = page.get_parent()
        if parent_page:
            # Verificar se já foi processado para evitar duplicação
            if parent_page.title in page.slug and ("recorrente" in page.slug or page.date.strftime('%Y-%m-%d') in page.slug):
                return
            
            # Processar apenas agendas recorrentes
            if page.habilitar_recorrencia and page.tipo_recorrencia != 'none':
                # Atualizar título e slug (removerá sufixos antigos se existirem)
                atualizar_titulo_slug_agenda_recorrente(page, parent_page, is_new=False)
            
                try:
                    new_revision = page.save_revision()
                    if page.live:
                        # Ensure that the updated title is on the published version
                        new_revision.publish()
                        
                except Exception as e:
                    error_message = processar_erro_agenda(e)
                    messages.error(request, error_message)