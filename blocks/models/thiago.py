from wagtail.blocks import StructBlock, ListBlock, URLBlock, CharBlock


class AcessoRapidoItemBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100)
    link = URLBlock(required=True)
    icone = CharBlock(required=False, help_text="Classe do ícone (ex: fas fa-car)")

    class Meta:
        icon = 'link'
        label = "Item de Acesso Rápido"

class AcessosRapidosBlock(StructBlock):
    itens = ListBlock(AcessoRapidoItemBlock(), default=[])

    class Meta:
        icon = 'list-ul'
        label = "Bloco de Acessos Rápidos"
        template = 'home/blocks/list_acesso_rapido.html'
        
