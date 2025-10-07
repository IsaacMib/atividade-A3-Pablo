from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import FormularioSubmissao

class FormularioSubmissaoViewSet(SnippetViewSet):
    model = FormularioSubmissao
    menu_label = "Formulário Contato"
    icon = "list-ul"
    menu_order = 200
    add_to_admin_menu = True
    list_display = ("nome_completo", "titulo", "pagina", "data_envio")
    list_filter = ("pagina", "data_envio")
    search_fields = ("nome_completo", "titulo", "dados_adicionais")
    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        return [url for url in urls if url.name in ('list', 'inspect')]

register_snippet(FormularioSubmissaoViewSet)