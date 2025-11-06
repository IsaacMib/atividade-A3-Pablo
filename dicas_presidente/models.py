from datetime import datetime
from django.db import models
from django.utils.safestring import mark_safe
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
    """Bloco para notícia interna (conquista, meta, evento, comunicado)."""
    
    CATEGORIA_CHOICES = [
        ('conquista', 'Conquista'),
        ('meta', 'Meta Alcançada'),
        ('evento', 'Evento'),
        ('comunicado', 'Comunicado Oficial'),
    ]
    
    categoria = ChoiceBlock(
        choices=CATEGORIA_CHOICES,
        required=False,
        label="Categoria da Notícia",
        help_text="Tipo de notícia interna."
    )
    conteudo = RichTextBlock(
        verbose_name="Conteúdo da Notícia",
        help_text="Corpo completo da notícia interna."
    )
    
    class Meta:
        icon = 'doc-full'
        label = 'Notícia Interna'
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
    
    # Imagem de destaque (para todos os tipos)
    imagem_destaque = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem de Destaque",
        help_text="Imagem principal da dica (usada em cards e compartilhamento)."
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
        FieldPanel("imagem_destaque"),
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
    
    def get_imagem_principal(self):
        """Retorna a imagem de destaque ou primeira imagem encontrada nos blocos."""
        if self.imagem_destaque:
            return self.imagem_destaque
        
        # Busca imagem na galeria
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
        icons_map = {
            'mensagem': '<i class="bi bi-chat-dots"></i>',
            'recomendacao': '<i class="bi bi-journal-check"></i>',
            'noticia_interna': '<i class="bi bi-newspaper"></i>',
            'galeria': '<i class="bi bi-camera"></i>',
            'frase': '<i class="bi bi-chat-quote"></i>',
        }
        tipos = self.get_tipos_blocos()
        icones = [icons_map.get(tipo, '') for tipo in tipos if tipo in icons_map]
        return mark_safe(' '.join(icones))
    
    def get_todas_labels_tipos(self):
        """Retorna todas as labels dos tipos de blocos presentes, separadas por ' • '."""
        tipo_map = {
            'mensagem': 'Mensagem Pessoal',
            'recomendacao': 'Recomendação/Estudo',
            'noticia_interna': 'Notícia Interna',
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
            'noticia_interna': 'Notícia Interna',
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
        """Retorna ícone baseado no tipo do primeiro bloco."""
        icons = {
            'mensagem': '<i class="bi bi-chat-dots"></i>',
            'recomendacao': '<i class="bi bi-journal-check"></i>',
            'noticia_interna': '<i class="bi bi-newspaper"></i>',
            'galeria': '<i class="bi bi-camera"></i>',
            'frase': '<i class="bi bi-chat-quote"></i>',
        }
        tipo = self.get_tipo_dica_principal()
        return mark_safe(icons.get(tipo, '<i class="bi bi-pin-angle"></i>'))
    
    def get_admin_display_title(self):
        """Exibe ícone do tipo + ★ se destaque."""
        title = super().get_admin_display_title()
        icon = self.get_tipo_dica_display_icon()
        star = "★ " if self.destaque else ""
        return f"{star}{icon} {title}"
    
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
        """Retorna dicas marcadas como destaque."""
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
        
        # Busca todas as dicas usando função centralizada
        dicas = self.get_todas_dicas()
        
        # Paginação
        paginator = Paginator(dicas, 12)
        page = request.GET.get("page")
        
        try:
            posts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            posts = paginator.page(1)
        
        # Contexto - todas as queries centralizadas
        context["posts"] = posts
        context["dicas_destaque"] = self.get_dicas_destaque()
        context["frase_aleatoria"] = self.get_frase_aleatoria()
        
        return context
