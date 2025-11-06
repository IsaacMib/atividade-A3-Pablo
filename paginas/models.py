from django.db import models
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
# from blocks.corpo_tecnico import ListGrupoCorpoTecnicoBlock  # Removido - cada app implementa seu próprio block
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from blocks.models import BaseStreamCorpoTecnicoBlock
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from wagtail.models.panels import PanelPlaceholder

from wagtail.blocks import (
    StructBlock,
    CharBlock,
    RichTextBlock,
)

# Create your models here.

class CorpoTecnicoIndexPage(PageSitePadraoIndex):

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

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel('tecnico_em_destaque'),
        # FieldPanel('grupos_corpo_tecnico'),  # Comentado - cada classe filha implementa seu próprio
    ]

class CorpoTecnicoGrupoPageIndex(PageSitePadraoIndex):
    
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

class CorpoTecnicoPage(PageSitePadrao):

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


class PaginaComBannerPage(PageSitePadrao):

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

    content_panels = PageSitePadrao.content_panels + [
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