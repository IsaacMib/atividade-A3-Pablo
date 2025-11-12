from datetime import datetime
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from wagtail.models import Page
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.fields import StreamField, RichTextField
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import (
    ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import (
    StructBlock, CharBlock, TextBlock, URLBlock, 
    StreamBlock, ChoiceBlock, RichTextBlock, ListBlock
)

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from core.models import PageSitePadrao, PageSitePadraoIndex
from blocks.models import BaseStreamBlock, EspecificDocumentChooserBlock
from core.utils import (
    get_page_title_with_counter,
    get_widget_input_with_counter
)


# ============================================================
# BLOCOS PERSONALIZADOS PARA DICAS DO PRESIDENTE
# ============================================================

class MensagemPresidenteBlock(StructBlock):
    """Bloco para mensagem pessoal do presidente."""
    texto = RichTextBlock(
        verbose_name="Texto da Mensagem",
        help_text="Mensagem motivacional ou comunicado do presidente."
    )
    assinatura = CharBlock(
        required=False,
        max_length=100,
        label="Assinatura",
        help_text="Ex: 'João Silva, Presidente'"
    )
    
    class Meta:
        icon = 'doc-full'
        label = 'Mensagem Pessoal'
        template = 'dicas_presidente/blocks/mensagem_presidente_block.html'


class RecomendacaoPresidenteBlock(StructBlock):
    """Bloco para recomendação de conteúdo (artigo, vídeo, livro, etc)."""
    
    TIPO_CHOICES = [
        ('artigo', 'Artigo'),
        ('video', 'Vídeo'),
        ('podcast', 'Podcast'),
        ('livro', 'Livro'),
        ('estudo', 'Estudo/Relatório'),
    ]
    
    tipo = ChoiceBlock(
        choices=TIPO_CHOICES,
        label="Tipo de Recomendação",
        help_text="Tipo de conteúdo recomendado."
    )
    link_externo = URLBlock(
        required=False,
        label="Link Externo",
        help_text="URL do artigo, vídeo, livro ou estudo recomendado."
    )
    texto_link = CharBlock(
        required=False,
        max_length=200,
        label="Texto do Link",
        help_text="Texto customizado para o botão (deixe vazio para usar 'Acessar conteúdo recomendado')."
    )
    motivo = TextBlock(
        required=False,
        label="Por que recomendo",
        help_text="Breve explicação do presidente sobre a recomendação."
    )
    conteudo_adicional = RichTextBlock(
        required=False,
        blank=True,
        verbose_name="Conteúdo Adicional",
        help_text="Informações extras sobre a recomendação."
    )
    
    class Meta:
        icon = 'doc-full'
        label = 'Recomendação/Estudo'
        template = 'dicas_presidente/blocks/recomendacao_presidente_block.html'


class NoticiaInternaPresidenteBlock(StructBlock):
    """Bloco para post interno (conquista, meta, evento, comunicado)."""
    
    CATEGORIA_CHOICES = [
        ('conquista', 'Conquista'),
        ('meta', 'Meta Alcançada'),
        ('evento', 'Evento'),
        ('comunicado', 'Comunicado Oficial'),
    ]
    
    categoria = ChoiceBlock(
        choices=CATEGORIA_CHOICES,
        required=False,
        label="Categoria do Post",
        help_text="Tipo de post interno."
    )
    conteudo = RichTextBlock(
        verbose_name="Conteúdo do Post",
        help_text="Corpo completo do post interno."
    )
    
    class Meta:
        icon = 'doc-full'
        label = 'Post Interno'
        template = 'dicas_presidente/blocks/noticia_interna_presidente_block.html'


class GaleriaPresidenteBlock(StructBlock):
    """Bloco para galeria de imagens (bastidores, eventos, visitas)."""
    imagens = ListBlock(
        ImageChooserBlock(label="Imagem"),
        label="Galeria de Imagens",
        help_text="Fotos de eventos, visitas, bastidores."
    )
    legenda = TextBlock(
        required=False,
        label="Legenda da Galeria",
        help_text="Descrição geral da galeria de imagens."
    )
    
    class Meta:
        icon = 'image'
        label = 'Galeria/Bastidores'
        template = 'dicas_presidente/blocks/galeria_presidente_block.html'


class FrasePresidenteBlock(StructBlock):
    """Bloco para frase inspiradora da semana."""
    texto_frase = TextBlock(
        label="Frase Inspiradora",
        help_text="Frase motivacional ou provocativa."
    )
    autor = CharBlock(
        required=False,
        max_length=100,
        label="Autor da Frase",
        help_text="Quem disse a frase (opcional)."
    )
    
    class Meta:
        icon = 'openquote'
        label = 'Frase da Semana'
        template = 'dicas_presidente/blocks/frase_presidente_block.html'


# StreamBlock principal que agrupa todos os tipos de dica
class DicaPresidenteStreamBlock(StreamBlock):
    """StreamBlock principal para conteúdo de dicas do presidente."""
    mensagem = MensagemPresidenteBlock()
    recomendacao = RecomendacaoPresidenteBlock()
    noticia_interna = NoticiaInternaPresidenteBlock()
    galeria = GaleriaPresidenteBlock()
    frase = FrasePresidenteBlock()


# ============================================================
# TAGS
# ============================================================

class DicasPresidentePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "DicasPresidentePage",
        related_name="tagged_items",
        on_delete=models.CASCADE
    )


# ============================================================
# PÁGINA INDIVIDUAL - DICA DO PRESIDENTE
# ============================================================

class DicasPresidentePage(PageSitePadrao):
    """
    Página individual de uma dica do presidente.
    Usa StreamField para flexibilidade - cada dica pode ter múltiplos blocos.
    """
    
    descricao = models.TextField(
        "Descrição/Resumo",
        help_text="Breve descrição ou resumo do conteúdo (aparece nas listagens).",
        max_length=255
    )
    
    data_publicacao = models.DateTimeField(
        "Data de publicação",
        default=datetime.now,
        blank=True,
        null=True
    )
    
    tags = ClusterTaggableManager(through=DicasPresidentePageTag, blank=True)
    
    destaque = models.BooleanField(
        "Dica em destaque",
        default=False,
        help_text="Marque para exibir esta dica em destaque na página principal."
    )
    
    # Coleção de imagens (seguindo padrão de notícias e avisos)
    imagens_dica = StreamField(
        [("imagem", ImageChooserBlock(required=True, label="Imagem da dica"))],
        verbose_name="Imagens da Dica",
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Adicione uma ou mais imagens para a dica."
    )
    
    slideshow_imagens = models.BooleanField(
        "Ativar slideshow de imagens",
        default=False,
        help_text="Exibir as imagens como slideshow.",
    )
    
    # Conteúdo principal usando StreamField
    conteudo = StreamField(
        DicaPresidenteStreamBlock(),
        verbose_name="Conteúdo",
        use_json_field=True,
        blank=True,
        help_text="Adicione um ou mais blocos para compor a dica."
    )
    
    # Arquivos anexos (opcional)
    arquivos = StreamField(
        [("arquivo", EspecificDocumentChooserBlock(required=True, label="Arquivo"))],
        verbose_name="Arquivos Anexos",
        blank=True,
        null=True,
        use_json_field=True,
        help_text="PDFs, apresentações ou documentos relacionados."
    )
    
    content_panels = get_page_title_with_counter(100) + [
        FieldPanel("destaque"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        MultiFieldPanel(
            [
                FieldPanel("slideshow_imagens"),
                FieldPanel("imagens_dica"),
            ],
            heading="Imagens da Dica",
        ),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
        FieldPanel("conteudo"),
        FieldPanel("arquivos"),
    ]
    
    promote_panels = PageSitePadrao.promote_panels
    settings_panels = PageSitePadrao.settings_panels
    
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Conteúdo"),
        ObjectList(promote_panels, heading="Promoções"),
        ObjectList(settings_panels, heading="Configurações"),
    ])
    
    parent_page_types = ["DicasPresidenteIndexPage"]
    subpage_types = []
    
    class Meta:
        verbose_name = "Dica do Presidente"
        verbose_name_plural = "Dicas do Presidente"
    
    icon = "doc-full"
    
    @property
    def is_remote(self):
        """Indica se a dica é remota (vindo de API externa). Sempre False para dicas locais."""
        return False
    
    def clean(self):
        super().clean()
        if len(self.title) > 100:
            raise ValidationError(
                {"title": "O título não pode ter mais que 100 caracteres."}
            )
    
    @property
    def get_tags(self):
        """Retorna as tags com suas URLs completas."""
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags
    
    @property
    def images(self):
        """
        Propriedade para compatibilidade com o template.
        Retorna o campo imagens_dica.
        """
        return self.imagens_dica
    
    def get_imagem_principal(self):
        """Retorna a primeira imagem da dica ou primeira imagem encontrada nos blocos."""
        # Primeiro tenta pegar da coleção de imagens da dica
        if self.imagens_dica and len(self.imagens_dica):
            for bloco in self.imagens_dica:
                if bloco.block_type == "imagem" and bloco.value:
                    return bloco.value
        
        # Busca imagem na galeria do conteúdo
        for bloco in self.conteudo:
            if bloco.block_type == "galeria" and bloco.value.get('imagens'):
                imagens = bloco.value.get('imagens')
                if imagens and len(imagens) > 0:
                    return imagens[0]
        
        return None
    
    def get_tipo_dica_principal(self):
        """Retorna o tipo do primeiro bloco de conteúdo."""
        if self.conteudo and len(self.conteudo) > 0:
            primeiro_bloco = self.conteudo[0]
            return primeiro_bloco.block_type
        return None
    
    def get_tipos_blocos(self):
        """Retorna lista de todos os tipos de blocos presentes na dica."""
        tipos = []
        if self.conteudo:
            for bloco in self.conteudo:
                if bloco.block_type not in tipos:
                    tipos.append(bloco.block_type)
        return tipos
    
    def get_todos_icones_tipos(self):
        """Retorna todos os ícones dos tipos de blocos presentes."""
        tipos = self.get_tipos_blocos()
        
        # Se houver múltiplos tipos, usa ícone de caneta para conteúdo misto
        if len(tipos) > 1:
            return mark_safe('<i class="bi bi-pen"></i>')
        
        # Se houver apenas um tipo, retorna o ícone específico
        icons_map = {
            'mensagem': '<i class="bi bi-chat-dots"></i>',
            'recomendacao': '<i class="bi bi-journal-check"></i>',
            'noticia_interna': '<i class="bi bi-newspaper"></i>',
            'galeria': '<i class="bi bi-camera"></i>',
            'frase': '<i class="bi bi-chat-quote"></i>',
        }
        
        if len(tipos) == 1:
            return mark_safe(icons_map.get(tipos[0], '<i class="bi bi-pin-angle"></i>'))
        
        return mark_safe('<i class="bi bi-pin-angle"></i>')
    
    def get_todas_labels_tipos(self):
        """Retorna todas as labels dos tipos de blocos presentes, separadas por ' • '."""
        tipo_map = {
            'mensagem': 'Mensagem Pessoal',
            'recomendacao': 'Recomendação/Estudo',
            'noticia_interna': 'Post Interno',
            'galeria': 'Galeria/Bastidores',
            'frase': 'Frase da Semana',
        }
        tipos = self.get_tipos_blocos()
        labels = [tipo_map.get(tipo, '') for tipo in tipos if tipo in tipo_map]
        return ' • '.join(labels)
    
    def get_tipo_dica_display(self):
        """Retorna o nome legível do tipo de dica ou todos os tipos se houver múltiplos."""
        tipo_map = {
            'mensagem': 'Mensagem Pessoal',
            'recomendacao': 'Recomendação/Estudo',
            'noticia_interna': 'Post Interno',
            'galeria': 'Galeria/Bastidores',
            'frase': 'Frase da Semana',
        }
        
        tipos = self.get_tipos_blocos()
        
        if len(tipos) > 1:
            # Múltiplos tipos: retorna "Conteúdo Misto"
            return 'Conteúdo Misto'
        elif len(tipos) == 1:
            # Um único tipo: retorna o nome
            return tipo_map.get(tipos[0], 'Dica do Presidente')
        else:
            # Sem conteúdo
            return 'Dica do Presidente'
    
    def get_tipo_dica_display_icon(self):
        """Retorna ícone SVG baseado no tipo do primeiro bloco."""
        icons = {
            'mensagem': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M5 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0m4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0m3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/><path d="m2.165 15.803.02-.004c1.83-.363 2.948-.842 3.468-1.105A9 9 0 0 0 8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6a10.4 10.4 0 0 1-.524 2.318l-.003.011a11 11 0 0 1-.244.637c-.079.186.074.394.273.362a22 22 0 0 0 .693-.125m.8-3.108a1 1 0 0 0-.287-.801C1.618 10.83 1 9.468 1 8c0-3.192 3.004-6 7-6s7 2.808 7 6-3.004 6-7 6a8 8 0 0 1-2.088-.272 1 1 0 0 0-.711.074c-.387.196-1.24.57-2.634.893a11 11 0 0 0 .398-2"/></svg>',
            'recomendacao': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M10.854 6.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7.5 8.793l2.646-2.647a.5.5 0 0 1 .708 0"/><path d="M3 0h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-1h1v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v1H1V2a2 2 0 0 1 2-2"/><path d="M1 5v-.5a.5.5 0 0 1 1 0V5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0V8h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0v.5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1z"/></svg>',
            'noticia_interna': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M0 2.5A1.5 1.5 0 0 1 1.5 1h11A1.5 1.5 0 0 1 14 2.5v10.528c0 .3-.05.654-.238.972h.738a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 1 1 0v9a1.5 1.5 0 0 1-1.5 1.5H1.497A1.497 1.497 0 0 1 0 13.5zM12 14c.37 0 .654-.211.853-.441.092-.106.147-.279.147-.531V2.5a.5.5 0 0 0-.5-.5h-11a.5.5 0 0 0-.5.5v11c0 .278.223.5.497.5z"/><path d="M2 3h10v2H2zm0 3h4v3H2zm0 4h4v1H2zm0 2h4v1H2zm5-6h2v1H7zm3 0h2v1h-2zM7 8h2v1H7zm3 0h2v1h-2zm-3 2h2v1H7zm3 0h2v1h-2zm-3 2h2v1H7zm3 0h2v1h-2z"/></svg>',
            'galeria': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M15 12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h1.172a3 3 0 0 0 2.12-.879l.83-.828A1 1 0 0 1 6.827 3h2.344a1 1 0 0 1 .707.293l.828.828A3 3 0 0 0 12.828 5H14a1 1 0 0 1 1 1zM2 4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-1.172a2 2 0 0 1-1.414-.586l-.828-.828A2 2 0 0 0 9.172 2H6.828a2 2 0 0 0-1.414.586l-.828.828A2 2 0 0 1 3.172 4z"/><path d="M8 11a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5m0 1a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7M3 6.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0"/></svg>',
            'frase': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M2.678 11.894a1 1 0 0 1 .287.801 11 11 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8 8 0 0 0 8 14c3.996 0 7-2.807 7-6s-3.004-6-7-6-7 2.808-7 6c0 1.468.617 2.83 1.678 3.894m-.493 3.905a22 22 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a10 10 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9 9 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105"/><path d="M7.066 6.76A1.665 1.665 0 0 0 4 7.668a1.667 1.667 0 0 0 2.561 1.406c-.131.389-.375.804-.777 1.22a.417.417 0 0 0 .6.58c1.486-1.54 1.293-3.214.682-4.112zm4 0A1.665 1.665 0 0 0 8 7.668a1.667 1.667 0 0 0 2.561 1.406c-.131.389-.375.804-.777 1.22a.417.417 0 0 0 .6.58c1.486-1.54 1.293-3.214.682-4.112z"/></svg>',
        }
        tipo = self.get_tipo_dica_principal()
        return format_html(icons.get(tipo, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M9.828.722a.5.5 0 0 1 .354.146l4.95 4.95a.5.5 0 0 1 0 .707c-.48.48-1.072.588-1.503.588-.177 0-.335-.018-.46-.039l-3.134 3.134a6 6 0 0 1 .16 1.013c.046.702-.032 1.687-.72 2.375a.5.5 0 0 1-.707 0l-2.829-2.828-3.182 3.182c-.195.195-1.219.902-1.414.707s.512-1.22.707-1.414l3.182-3.182-2.828-2.829a.5.5 0 0 1 0-.707c.688-.688 1.673-.767 2.375-.72a6 6 0 0 1 1.013.16l3.134-3.133a3 3 0 0 1-.04-.461c0-.43.108-1.022.589-1.503a.5.5 0 0 1 .353-.146m.122 2.112v-.002zm0-.002v.002a.5.5 0 0 1-.122.51L6.293 6.878a.5.5 0 0 1-.511.12H5.78l-.014-.004a5 5 0 0 0-.288-.076 5 5 0 0 0-.765-.116c-.422-.028-.836.008-1.175.15l5.51 5.509c.141-.34.177-.753.149-1.175a5 5 0 0 0-.192-1.054l-.004-.013v-.001a.5.5 0 0 1 .12-.512l3.536-3.535a.5.5 0 0 1 .532-.115l.096.022c.087.017.208.034.344.034q.172.002.343-.04L9.927 2.028q-.042.172-.04.343a1.8 1.8 0 0 0 .062.46z"/></svg>'))
    
    def eh_frase(self):
        """Verifica se a dica é do tipo frase (para widgets)."""
        return self.get_tipo_dica_principal() == 'frase'
    
    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('descricao'),
        index.SearchField('conteudo'),
    ]


# ============================================================
# PÁGINA INDEX - LISTAGEM DE DICAS
# ============================================================

class DicasPresidenteIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    """Página principal de Dicas do Presidente com listagem e filtros."""
    
    introduction = models.TextField(
        "Introdução",
        blank=True,
        help_text="Texto de apresentação no topo da página."
    )
    
    mensagem_presidente = models.TextField(
        "Mensagem do Presidente",
        blank=True,
        help_text="Mensagem introdutória do presidente (aparece em destaque)."
    )
    
    foto_presidente = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Foto do Presidente",
        help_text="Foto para o banner da página."
    )
    
    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel([
            FieldPanel("foto_presidente"),
            FieldPanel("mensagem_presidente"),
        ], heading="Banner do Presidente"),
    ]
    
    parent_page_types = ["intranet.IntranetHomePage", "home.HomePage"]
    subpage_types = ["DicasPresidentePage"]
    
    class Meta:
        verbose_name = "Página de Índice - Dicas do Presidente"
        verbose_name_plural = "Páginas de Índice - Dicas do Presidente"
    
    icon = "folder-open-inverse"
    
    def get_dicas_destaque(self, quantidade=3):
        return (
            DicasPresidentePage.objects.live()
            .descendant_of(self)
            .filter(destaque=True)
            .order_by("-data_publicacao")[:quantidade]
        )
    
    def get_todas_dicas(self):
        """
        Retorna todas as dicas publicadas, ordenadas por data.
        Função centralizada para buscar dicas - todas as modificações
        de filtros e ordenação devem ser feitas aqui.
        """
        return (
            DicasPresidentePage.objects.live()
            .descendant_of(self)
            .order_by("-data_publicacao")
        )
    
    def get_ultimas_dicas(self, quantidade=6):
        """
        Retorna as últimas N dicas publicadas.
        Usa get_todas_dicas() como base para manter consistência.
        """
        return self.get_todas_dicas()[:quantidade]
    
    def get_frases_aleatorias(self):
        """Retorna todas as dicas que contêm blocos de frase."""
        dicas = self.get_todas_dicas()
        frases = []
        for dica in dicas:
            for bloco in dica.conteudo:
                if bloco.block_type == 'frase':
                    frases.append({
                        'dica': dica,
                        'bloco': bloco,
                        'texto': bloco.value.get('texto_frase', ''),
                        'autor': bloco.value.get('autor', ''),
                    })
        return frases
    
    def get_frase_aleatoria(self):
        """Retorna uma frase aleatória para widget."""
        import random
        frases = self.get_frases_aleatorias()
        if frases:
            return random.choice(frases)
        return None
    
    def get_context(self, request):
        """Adiciona dicas paginadas ao contexto."""
        context = super().get_context(request)
        
        # Busca dicas de destaque (fixas no topo)
        dicas_destaque = self.get_dicas_destaque()
        
        # Busca todas as dicas EXCLUINDO as que estão em destaque
        # para evitar duplicação na listagem
        dicas_destaque_ids = [dica.id for dica in dicas_destaque]
        dicas = self.get_todas_dicas().exclude(id__in=dicas_destaque_ids)
        
        # Paginação
        paginator = Paginator(dicas, 12)
        page = request.GET.get("page")
        
        try:
            posts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            posts = paginator.page(1)
        
        # Contexto - todas as queries centralizadas
        context["posts"] = posts
        context["dicas_destaque"] = dicas_destaque
        context["frase_aleatoria"] = self.get_frase_aleatoria()
        
        return context
