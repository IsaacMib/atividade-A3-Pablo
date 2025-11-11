import locale
import ast

from wagtail import hooks
from agenda.models import AgendaDoDiaPage
from django.utils.text import slugify
from wagtail.admin import messages
from django.shortcuts import redirect
from django.contrib import messages as django_messages

# Configurar o locale para PT-BR
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

@hooks.register('after_publish_page')
@hooks.register('after_create_page')
def do_after_agendadodia_page_edit(request, page):
    if isinstance(page, AgendaDoDiaPage):
        # Apenas processar agendas recorrentes
        if not (page.habilitar_recorrencia and page.tipo_recorrencia != 'none'):
            return
            
        parent_page = page.get_parent()
        if parent_page:
            # Verificar se o título do pai já está no slug para evitar duplicação
            if parent_page.title in page.slug and "recorrente" in page.slug:
                return
            
            # Guardar o título e slug originais da agenda
            titulo_original = page.title
            slug_original = page.slug
            
            # Atualizar o slug para incluir "recorrente" se ainda não tiver
            if "recorrente" not in slug_original:
                page.slug = slugify(f"{slug_original}-recorrente")

            # Mapear tipos de recorrência para texto descritivo
            if page.tipo_recorrencia == 'days' and page.intervalo_recorrencia == 7:
                tipo_recorrencia_texto = 'Semanal'
            else:
                tipo_recorrencia_texto = {
                    'days': 'Diária',
                    'months': 'Mensal',  
                    'years': 'Anual'
                }.get(page.tipo_recorrencia, page.tipo_recorrencia.title())
            
            # Atualizar o título para incluir o título do pai, título original e tipo de recorrência
            page.title = f"{parent_page.title} - {titulo_original} - Agenda Recorrente {tipo_recorrencia_texto}"
            
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
                # Tentar tratar error_message como JSON e extrair o campo 'slug'
                # Corrigir aspas simples para aspas duplas
                error_message = str(e)
                try:
                    data = ast.literal_eval(error_message)
                    if 'slug' in data:
                        error_message = data['slug'][0]
                except:
                    pass  # Se não conseguir fazer parse, usa a mensagem original

                # Remover mensagens existentes
                list(django_messages.get_messages(request))

                # Remover a página em caso de erro
                page.delete()
                messages.error(request, error_message)
                # Redirecionar para wagtailadmin_explore com parent_page_id
                return redirect("wagtailadmin_explore", parent_page_id=parent_page.id)