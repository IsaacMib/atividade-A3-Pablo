from wagtail.blocks import StructBlock, ListBlock, URLBlock, CharBlock
from wagtail.images.blocks import ImageChooserBlock


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
        
class BannerComLinkBlock(StructBlock):
    imagem = ImageChooserBlock(required=True, label="Imagem do Banner")
    link = URLBlock(required=True, label="URL do Banner")
    alt_texto = CharBlock(required=False, label="Texto alternativo", help_text="Descrição da imagem (alt)")

    class Meta:
        icon = 'image'
        label = "Banner com Link"
        template = 'home/blocks/banner.html'