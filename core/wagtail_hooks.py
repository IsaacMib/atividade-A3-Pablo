from wagtail import hooks
from agenda.models import AgendaIndexPage
from noticias.models import NoticiasIndexPages
from avisos.models import AvisosIndexPage
from wagtail.admin import messages
from django.shortcuts import redirect

@hooks.register('before_create_page')
def do_before_agendaindex_page_edit(request, parent_page, page_class):
    tipos_unicos = [AgendaIndexPage, AvisosIndexPage, NoticiasIndexPages]
    if page_class in tipos_unicos:
        # Verifica se já existe um filho do mesmo tipo para o parent_page
        if parent_page.get_children().type(page_class).exists():
            messages.error(
                request,
                f"Já existe uma página do tipo {page_class._meta.verbose_name} para este local. Só é permitido um por pai."
            )
            return redirect("wagtailadmin_explore", parent_page_id=parent_page.id)