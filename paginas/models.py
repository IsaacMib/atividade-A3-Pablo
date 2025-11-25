from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.admin.panels import FieldPanel, TitleFieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models.panels import PanelPlaceholder

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from core.models import PageNeuroAthena, PageNeuroAthenaIndex
from blocks.models import BaseStreamBlock, BaseStreamCorpoTecnicoBlock, EspecificDocumentChooserBlock, BaseRichTextStreamBlock
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter
)

from wagtail.blocks import (
    StructBlock,
    CharBlock,
    RichTextBlock,
)

# Create your models here.

# ============================================================
#                   CORPO TÉCNICO
# ============================================================

class CorpoTecnicoIndexPage(PageNeuroAthenaIndex):

    class Meta:
        abstract = True

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    subpage_types = ['paginas.CorpoTecnicoGrupoPageIndex']

    sub_titulo = models.CharField(
        verbose_name="Subtítulo",
        max_length=255,
        blank=True,
        null=True,
        help_text="Subtítulo da página do corpo técnico."
    )

    tecnico_em_destaque = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Técnico em Destaque",
        help_text="Selecione um membro do corpo técnico para destacar na página inicial do corpo técnico."
    )

    # grupos_corpo_tecnico comentado pois usa block genérico com referência abstrata
    # Cada classe filha deve implementar seu próprio campo com block específico
    # grupos_corpo_tecnico = StreamField(
    #     [
    #         ('grupo', ListGrupoCorpoTecnicoBlock(label="Grupo do Corpo Técnico")),
    #     ],
    #     verbose_name="Grupos do Corpo Técnico",
    #     null=True,
    #     blank=True,
    # )

    content_panels = PageNeuroAthenaIndex.content_panels + [
        FieldPanel('tecnico_em_destaque'),
        # FieldPanel('grupos_corpo_tecnico'),  # Comentado - cada classe filha implementa seu próprio
    ]

class CorpoTecnicoGrupoPageIndex(PageNeuroAthenaIndex):
    
    class Meta:
        abstract = True

    parent_page_types = [ 'paginas.CorpoTecnicoIndexPage' ]
    subpage_types = ['paginas.CorpoTecnicoPage']

    def get_context(self, request):
        context = super(CorpoTecnicoGrupoPageIndex, self).get_context(request)
        all_posts = CorpoTecnicoPage.objects.descendant_of(
            self).live().order_by("title")
        paginator = Paginator(all_posts, 8)  # 8 membros por página
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context["posts"] = posts
        return context
    
    def get_corpo_tecnico(self, quantidade=8):
        """
        Retorna os filhos (CorpoTecnicoPage) ordenados por título.
        
        Args:
            quantidade (int): Número de itens a retornar. Padrão é 6.
        
        Returns:
            QuerySet: Lista de páginas CorpoTecnicoPage limitada pela quantidade especificada.
        """
        return CorpoTecnicoPage.objects.descendant_of(self).live().order_by('title')[:quantidade]

class CorpoTecnicoPage(PageNeuroAthena):

    class Meta:
        abstract = True

    parent_page_types = [ 'paginas.CorpoTecnicoGrupoPageIndex' ]
    subpage_types = []

    funcao = models.CharField(
        verbose_name="Função",
        max_length=255,
        blank=True,
        null=True,
        help_text="Função ou cargo do membro do corpo técnico."
    )
    bio = StreamField(
        BaseStreamCorpoTecnicoBlock(), verbose_name="Biografia", blank=True, null=True, use_json_field=True
    )

    imagem = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Imagem",
        help_text="Imagem do membro do corpo técnico."
    )

    content_panels = [
        TitleFieldPanel('title', 
            placeholder="Nome do Membro", 
            help_text="Nome completo do membro do corpo técnico."),
        FieldPanel('funcao'),
        FieldPanel('imagem'),
        FieldPanel('bio'),
    ]

# Página genérica para uso em qualquer lugar do site
class RichTextPage(PageNeuroAthena):
        

    """
    Página que permite a criação de conteúdo rico usando StreamField.
    Herda de PageNeuroAthena para manter a consistência com o restante do site.
    """
    template = 'paginas/rich_text_page.html'
    
    # Campos do modelo
    body = StreamField(
        BaseRichTextStreamBlock(),  # Usa o BaseRichTextStreamBlock que já existe no seu projeto
        verbose_name="Conteúdo",
        use_json_field=True,
        blank=True,
        null=True,
        help_text="Adicione o conteúdo da página utilizando os blocos disponíveis."
    )
    
    # Painéis de conteúdo que aparecerão no admin do Wagtail
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('body'),
    ]
    
    # Configurações adicionais, os nomes que aparecerão no admin
    class Meta:
        abstract = True
        verbose_name = "Página de Texto Rico"
        verbose_name_plural = "Páginas de Texto Rico"

class PaginaComBannerPage(PageNeuroAthena):

    subtitle = models.CharField(
        verbose_name="Subtítulo",
        blank=True,
        max_length=255
    )   

    banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Banner da página"
    )

    introducao = models.TextField(
        verbose_name="Introdução",
        blank=True,
        help_text="Texto introdutório"
    )

    corpo = StreamField([
        ('titulo_texto', StructBlock([
            ('titulo', CharBlock(required=True, label="Título")),
            ('texto', RichTextBlock(required=True, label="Texto")),
        ], label="Título e Texto")),
    ], verbose_name="Conteúdo da página", blank=True, null=True, use_json_field=True)

    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel("subtitle"),        
        FieldPanel("banner"),  
        FieldPanel("introducao"),
        FieldPanel("corpo"),
    ]

    parent_page_types = ["home.HomePage"] 
    subpage_types = [] 

    class Meta:
        abstract = True
        verbose_name = "Pagina com Banner"
        verbose_name_plural = "Paginas com Banner"


class RedirectPage(PageNeuroAthena):
    """
    Página que redireciona para um link interno ou externo.
    - Usuários não autenticados: redirecionados automaticamente
    - Usuários autenticados: visualizam a página com informações do link
    
    Esta página pode ser criada em qualquer local do site (filha de qualquer Index).
    """
    
    # Link interno (página do Wagtail)
    internal_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Página interna",
        help_text="Selecione uma página interna do site para redirecionar"
    )
    
    # Link externo (URL)
    external_url = models.URLField(
        verbose_name="URL externa",
        blank=True,
        null=True,
        max_length=500,
        help_text="Ou insira uma URL externa (ex: https://exemplo.com)"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("internal_page"),
                FieldPanel("external_url"),
            ],
            heading="Destino do Redirect (escolha apenas um)",
            help_text="Preencha apenas um dos campos abaixo. Se ambos forem preenchidos, a página interna terá prioridade."
        ),
    ]
    
    subpage_types = []  # Não permite páginas filhas
    
    class Meta:
        verbose_name = "Página Link"
        verbose_name_plural = "Páginas Link"
    
    def clean(self):
        """Valida que apenas um tipo de link foi preenchido"""
        super().clean()
        
        has_internal = bool(self.internal_page)
        has_external = bool(self.external_url)
        
        if not has_internal and not has_external:
            raise ValidationError({
                'internal_page': 'Você deve fornecer um link interno ou externo.',
                'external_url': 'Você deve fornecer um link interno ou externo.'
            })
        
        if has_internal and has_external:
            raise ValidationError(
                'Você deve fornecer apenas UM link (interno OU externo), não ambos.'
            )
    
    def get_redirect_url(self):
        """Retorna a URL de redirecionamento"""
        if self.internal_page:
            return self.internal_page.url
        return self.external_url
    
    def serve(self, request):
        """
        Redireciona usuários não autenticados automaticamente.
        Usuários autenticados visualizam a página normalmente.
        """
        from django.shortcuts import redirect
        
        # Se o usuário NÃO está autenticado, redireciona
        if not request.user.is_authenticated:
            redirect_url = self.get_redirect_url()
            if redirect_url:
                return redirect(redirect_url)
        
        # Se está autenticado, renderiza a página normalmente
        return super().serve(request)
    
    def get_context(self, request):
        """Adiciona informações do redirect ao contexto"""
        context = super().get_context(request)
        context['redirect_url'] = self.get_redirect_url()
        context['is_internal'] = bool(self.internal_page)
        context['is_external'] = bool(self.external_url)
        return context


