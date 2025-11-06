from datetime import datetime
from django.db import models
from django.utils.safestring import mark_safe
from wagtail.models import Page
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import (
    ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
)
from wagtail.images.blocks import ImageChooserBlock

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
# CHOICES
# ============================================================

TIPO_DICA_CHOICES = [
    ('mensagem', 'Mensagem Pessoal'),
    ('recomendacao', 'Recomendação/Estudo'),
    ('noticia_interna', 'Notícia Interna'),
    ('galeria', 'Galeria/Bastidores'),
    ('frase', 'Frase da Semana'),
]

TIPO_RECOMENDACAO_CHOICES = [
    ('artigo', 'Artigo'),
    ('video', 'Vídeo'),
    ('podcast', 'Podcast'),
    ('livro', 'Livro'),
    ('estudo', 'Estudo/Relatório'),
]

CATEGORIA_NOTICIA_CHOICES = [
    ('conquista', 'Conquista'),
    ('meta', 'Meta Alcançada'),
    ('evento', 'Evento'),
    ('comunicado', 'Comunicado Oficial'),
]


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
    Pode ser: mensagem, recomendação, notícia interna, galeria ou frase.
    """
    
    tipo_dica = models.CharField(
        "Tipo de Dica",
        max_length=20,
        choices=TIPO_DICA_CHOICES,
        default='mensagem',
        help_text="Selecione o tipo de conteúdo desta dica."
    )
    
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
    
    # ============================================================
    # CAMPOS ESPECÍFICOS POR TIPO
    # ============================================================
    
    # Para Mensagem Pessoal
    texto_mensagem = StreamField(
        BaseStreamBlock(),
        verbose_name="Texto da Mensagem",
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Mensagem motivacional ou comunicado do presidente."
    )
    
    assinatura = models.CharField(
        "Assinatura",
        max_length=100,
        blank=True,
        help_text="Ex: 'João Silva, Presidente'"
    )
    
    # Para Recomendação/Estudo
    tipo_recomendacao = models.CharField(
        "Tipo de Recomendação",
        max_length=20,
        choices=TIPO_RECOMENDACAO_CHOICES,
        blank=True,
        help_text="Tipo de conteúdo recomendado."
    )
    
    link_externo = models.URLField(
        "Link Externo",
        blank=True,
        help_text="URL do artigo, vídeo, livro ou estudo recomendado."
    )
    
    motivo_recomendacao = models.TextField(
        "Por que recomendo",
        blank=True,
        help_text="Breve explicação do presidente sobre a recomendação."
    )
    
    # Para Notícia Interna
    categoria_noticia = models.CharField(
        "Categoria da Notícia",
        max_length=20,
        choices=CATEGORIA_NOTICIA_CHOICES,
        blank=True,
        help_text="Tipo de notícia interna."
    )
    
    body = StreamField(
        BaseStreamBlock(),
        verbose_name="Conteúdo Principal",
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Corpo completo da dica (textos, imagens, vídeos, etc)."
    )
    
    # Para Galeria/Bastidores
    galeria_imagens = StreamField(
        [("imagem", ImageChooserBlock(required=True, label="Imagem"))],
        verbose_name="Galeria de Imagens",
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Fotos de eventos, visitas, bastidores."
    )
    
    legenda_galeria = models.TextField(
        "Legenda da Galeria",
        blank=True,
        help_text="Descrição geral da galeria de imagens."
    )
    
    # Para Frase da Semana
    texto_frase = models.TextField(
        "Frase Inspiradora",
        blank=True,
        help_text="Frase motivacional ou provocativa."
    )
    
    autor_frase = models.CharField(
        "Autor da Frase",
        max_length=100,
        blank=True,
        help_text="Quem disse a frase (opcional)."
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
        FieldPanel("tipo_dica"),
        FieldPanel("destaque"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        FieldPanel("imagem_destaque"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
        
        # Campos condicionais por tipo (todos visíveis, admin escolhe quais preencher)
        MultiFieldPanel([
            FieldPanel("texto_mensagem"),
            FieldPanel("assinatura"),
        ], heading="Mensagem Pessoal", classname="collapsible"),
        
        MultiFieldPanel([
            FieldPanel("tipo_recomendacao"),
            FieldPanel("link_externo"),
            FieldPanel("motivo_recomendacao"),
        ], heading="Recomendação/Estudo", classname="collapsible"),
        
        MultiFieldPanel([
            FieldPanel("categoria_noticia"),
            FieldPanel("body"),
        ], heading="Notícia Interna", classname="collapsible"),
        
        MultiFieldPanel([
            FieldPanel("galeria_imagens"),
            FieldPanel("legenda_galeria"),
        ], heading="Galeria/Bastidores", classname="collapsible"),
        
        MultiFieldPanel([
            FieldPanel("texto_frase"),
            FieldPanel("autor_frase"),
        ], heading="Frase da Semana", classname="collapsible"),
        
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
        """Retorna a imagem de destaque ou primeira da galeria."""
        if self.imagem_destaque:
            return self.imagem_destaque
        
        if self.galeria_imagens:
            for bloco in self.galeria_imagens:
                if bloco.block_type == "imagem" and bloco.value:
                    return bloco.value
        return None
    
    def get_tipo_dica_display_icon(self):
        """Retorna ícone baseado no tipo de dica."""
        icons = {
            'mensagem': '<i class="bi bi-chat-dots-fill"></i>',
            'recomendacao': '<i class="bi bi-journal-check"></i>',
            'noticia_interna': '<i class="bi bi-newspaper"></i>',
            'galeria': '<i class="bi bi-camera"></i>',
            'frase': '<i class="bi bi-chat-quote"></i>',
        }
        return mark_safe(icons.get(self.tipo_dica, '<i class="bi bi-pin-angle"></i>'))
    
    def get_admin_display_title(self):
        """Exibe ícone do tipo + ★ se destaque."""
        title = super().get_admin_display_title()
        icon = self.get_tipo_dica_display_icon()
        star = "★ " if self.destaque else ""
        return f"{star}{icon} {title}"
    
    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('descricao'),
        index.SearchField('texto_mensagem'),
        index.SearchField('texto_frase'),
        index.SearchField('body'),
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
    
    mostrar_filtro_tipo = models.BooleanField(
        "Mostrar filtro por tipo",
        default=True,
        help_text="Permite filtrar dicas por tipo (mensagem, recomendação, etc)."
    )
    
    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel([
            FieldPanel("foto_presidente"),
            FieldPanel("mensagem_presidente"),
        ], heading="Banner do Presidente"),
        FieldPanel("mostrar_filtro_tipo"),
    ]
    
    parent_page_types = ["intranet.IntranetHomePage"]
    subpage_types = ["DicasPresidentePage"]
    
    class Meta:
        verbose_name = "Página de Índice - Dicas do Presidente"
        verbose_name_plural = "Páginas de Índice - Dicas do Presidente"
    
    icon = "folder-open-inverse"
    
    def get_dicas(self, tipo=None, tag=None):
        """Retorna dicas filtradas por tipo e/ou tag."""
        dicas = DicasPresidentePage.objects.live().descendant_of(self)
        
        if tipo:
            dicas = dicas.filter(tipo_dica=tipo)
        
        if tag:
            dicas = dicas.filter(tags=tag)
        
        return dicas.order_by("-data_publicacao")
    
    def get_dicas_destaque(self, quantidade=3):
        """Retorna dicas marcadas como destaque."""
        return (
            DicasPresidentePage.objects.live()
            .descendant_of(self)
            .filter(destaque=True)
            .order_by("-data_publicacao")[:quantidade]
        )
    
    def get_ultimas_dicas(self, quantidade=6):
        """
        Retorna as últimas dicas publicadas.
        Função centralizada para buscar dicas - modificações futuras
        (como adicionar filtro de destaque) devem ser feitas aqui.
        """
        return (
            DicasPresidentePage.objects.live()
            .descendant_of(self)
            .order_by("-data_publicacao")[:quantidade]
        )
    
    def get_frase_aleatoria(self):
        """Retorna uma frase aleatória para widget."""
        frases = (
            DicasPresidentePage.objects.live()
            .descendant_of(self)
            .filter(tipo_dica='frase')
            .order_by('?')
        )
        return frases.first() if frases.exists() else None
    
    def get_context(self, request):
        """Adiciona dicas paginadas e filtros ao contexto."""
        context = super().get_context(request)
        
        # Filtros
        tipo_filtro = request.GET.get("tipo")
        tag_slug = request.GET.get("tag")
        tag_obj = None
        
        if tag_slug:
            try:
                tag_obj = Tag.objects.get(slug=tag_slug)
            except Tag.DoesNotExist:
                pass
        
        # Busca dicas
        dicas = self.get_dicas(tipo=tipo_filtro, tag=tag_obj)
        
        # Paginação
        paginator = Paginator(dicas, 12)
        page = request.GET.get("page")
        
        try:
            posts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            posts = paginator.page(1)
        
        # Contexto
        context["posts"] = posts
        context["dicas_destaque"] = self.get_dicas_destaque()
        context["frase_aleatoria"] = self.get_frase_aleatoria()
        context["tipo_filtro"] = tipo_filtro
        context["tag"] = tag_obj
        context["tipos_dica"] = TIPO_DICA_CHOICES
        
        # Tags disponíveis
        context["tags"] = (
            Tag.objects.filter(
                dicas_presidente_dicaspresidentepagetag_items__content_object__live=True
            )
            .distinct()
            .order_by("name")
        )
        
        return context
    
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        """Rota para filtro por tag."""
        try:
            tag_obj = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                messages.info(request, f'Não há dicas com a tag "{tag}".')
            return redirect(self.url)
        
        dicas = self.get_dicas(tag=tag_obj)
        return render(request, "dicas_presidente/dicas_presidente_index_page.html", {
            "self": self,
            "tag": tag_obj,
            "posts": dicas,
        })
