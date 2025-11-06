from django.urls import reverse
from django.conf import settings
from wagtail import hooks
from agenda.models import AgendaIndexPage
from noticias.models import NoticiasIndexPages
from avisos.models import AvisosIndexPage
from contatos.models import ContatosPage
from wagtail.admin import messages
from django.shortcuts import redirect
from django.templatetags.static import static
from django.utils.html import format_html_join


@hooks.register('before_create_page')
def do_before_agendaindex_page_edit(request, parent_page, page_class):
    tipos_unicos = [AgendaIndexPage, AvisosIndexPage, NoticiasIndexPages, ContatosPage]
    if page_class in tipos_unicos:
        # Verifica se já existe um filho do mesmo tipo para o parent_page
        if parent_page.get_children().type(page_class).exists():
            messages.error(
                request,
                f"Já existe uma página do tipo {page_class._meta.verbose_name} para este local. Só é permitido um por pai."
            )
            return redirect("wagtailadmin_explore", parent_page_id=parent_page.id)


@hooks.register('insert_editor_js')
def editor_js():
    # Adicionar arquivo js para contagem de caracteres
    js_files = ['js/char-count-controller.js',]
    return format_html_join('\n', '<script src="{0}"></script>',
                            ((static(filename),) for filename in js_files)
                            )
