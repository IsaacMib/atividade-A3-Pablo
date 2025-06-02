from wagtail.blocks import StructBlock, ListBlock, URLBlock, CharBlock
from wagtail.images.blocks import ImageChooserBlock
from blocks.utils import ICONES_REDES, ICONES_ACESSO_RAPIDO
from django.db import models
from wagtail import blocks



class AcessoRapidoItemBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100)
    link = URLBlock(required=True)
    icone = blocks.ChoiceBlock(choices=ICONES_ACESSO_RAPIDO, required=True, label="Ícone")

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


class VideoBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100)
    srcIframe = URLBlock(required=True, label="URL do vídeo (iframe YouTube)")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        url = value.get('srcIframe')

        # Transforma links padrão do YouTube em formato embed
        if 'watch?v=' in url:
            url = url.replace('watch?v=', 'embed/')
        elif 'youtu.be/' in url:
            url = url.replace('youtu.be/', 'www.youtube.com/embed/')

        context['titulo'] = value.get('titulo')
        context['src'] = url
        return context

    class Meta:
        icon = 'media'
        label = "Vídeo"
        template = 'home/blocks/video.html'
        


class ListaVideosBlock(StructBlock):
    videos = ListBlock(VideoBlock(), label="Vídeos", max_num=3)
    ver_todos_url = URLBlock(required=False, label="URL do 'Ver todos'")

    class Meta:
        icon = 'list-ul'
        label = "Lista de Vídeos"
        template = 'home/blocks/list_video.html'

class RedeSocialItemBlock(StructBlock):
    nome = CharBlock(required=True)
    link = URLBlock(required=True)
    icone = blocks.ChoiceBlock(choices=ICONES_REDES, required=True)
    class Meta:
        icon = "site"
        label = "Bloco de Redes Sociais"
        template = "home/blocks/redes_sociais.html"

class ListRedeSocial(StructBlock):
   titulo = CharBlock(required=False, default="Siga-nos nas redes sociais")
   imagem = ImageChooserBlock(required=False, help_text="Imagem que será exibida ao lado do texto.")
   redes = ListBlock(RedeSocialItemBlock(), max_num=4)

   class Meta:
      icon = 'list-ul'
      label = "Lista de Redes Sociais"
      template = "home/blocks/redes_sociais.html"
