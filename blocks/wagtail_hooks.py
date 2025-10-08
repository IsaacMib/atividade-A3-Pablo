from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from .models import FormularioSubmissao

class FormularioSubmissaoViewSet(SnippetViewSet):
    model = FormularioSubmissao
    menu_label = "Formulário"
    icon = "form"
    menu_order = 200
    add_to_admin_menu = True
    list_display = ("nome_completo", "titulo", "pagina", "data_envio", "arquivos_para_download")
    list_filter = ("pagina", "data_envio")
    search_fields = ("nome_completo", "titulo", "dados_adicionais")
    inspect_view_enabled = True

    inspect_view_fields = [
        'nome_completo',
        'titulo',
        'pagina',
        'data_envio',
        'usuario',
        'dados_adicionais_formatados',
        'arquivos_para_download',
    ]
    add_view_enabled = False
    edit_view_enabled = False
    delete_view_enabled = False

register_snippet(FormularioSubmissaoViewSet)