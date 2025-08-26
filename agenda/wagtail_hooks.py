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
        parent_page = page.get_parent()
        if parent_page:
            # Verificar se o título do pai já está no slug
            if parent_page.title in page.slug:
                return
            
            # Atualizar o slug para ser uma composição do título do pai e a data
            page.slug = slugify(f"{parent_page.title}-{page.date.strftime('%Y-%m-%d')}")

            # Atualizar o título para incluir o título do pai e a data em formato extenso
            data_extensa = page.date.strftime("%d de %B")
            page.title = f"{parent_page.title} - Agenda do Dia {data_extensa}"
            
            try:
                new_revision = page.save_revision()
                if page.live:
                    # page has been created and published at the same time,
                    # so ensure that the updated title is on the published version too
                    new_revision.publish()
            except Exception as e:
                # Tentar tratar error_message como JSON e extrair o campo 'slug'
                # Corrigir aspas simples para aspas duplas
                error_message = str(e)
                data = ast.literal_eval(error_message)
                if 'slug' in data:
                    error_message = data['slug'][0]

                # Remover mensagens existentes
                list(django_messages.get_messages(request))

                # Remover a página em caso de erro
                page.delete()
                messages.error(request, error_message)
                # Redirecionar para wagtailadmin_explore com parent_page_id
                return redirect("wagtailadmin_explore", parent_page_id=parent_page.id)