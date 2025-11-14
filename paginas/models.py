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

from core.models import PageSitePadrao, PageSitePadraoIndex
from blocks.models import BaseStreamBlock, BaseStreamCorpoTecnicoBlock, EspecificDocumentChooserBlock
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
#                   CLASSE BASE ABSTRATA
# ============================================================

class AvisosDefaultPage(PageSitePadrao):
    """
    Classe base abstrata para páginas de Avisos e Eventos.
    Centraliza campos e métodos comuns para evitar duplicação de código.
    """
    descricao = models.TextField(
        "Descrição",
        help_text="Breve descrição do conteúdo da página.",
        max_length=255
    )

    data_publicacao = models.DateTimeField(
        "Data de publicação",
        default=datetime.now,
        blank=True,
        null=True
    )

    body = StreamField(
        BaseStreamBlock(),
        verbose_name="Corpo da página",
        blank=True,
        null=True,
        use_json_field=True
    )

    body_migrated = models.TextField(
        "Conteúdo migrado do Plone",
        help_text="Usado apenas para conteúdo do antigo site Plone.",
        blank=True,
        null=True
    )

    plone_node_id = models.TextField(
        "ID Plone",
        blank=True,
        null=True,
        db_index=True,
        unique=True,
        help_text="ID do nó no Plone, usado para identificar a página migrada."
    )

    sensivel_periodo_eleitoral = models.BooleanField(
        "Sensível ao período eleitoral",
        default=False,
        help_text="Marque se este conteúdo deve ser ocultado durante o período eleitoral."
    )

    arquivos = StreamField(
        [("arquivo", EspecificDocumentChooserBlock(required=True, label="Arquivos"))],
        verbose_name="Arquivos",
        blank=True,
        null=True,
        use_json_field=True,
    )

    nao_exibir_lista_de_arquivos = models.BooleanField(
        "Não exibir lista de arquivos",
        default=False,
        help_text="Marque para ocultar a lista de arquivos.",
    )

    content_panels = get_page_title_with_counter(100) + [
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        MultiFieldPanel(
            [
                FieldPanel("nao_exibir_lista_de_arquivos"),
                FieldPanel("arquivos"),
            ],
            heading="Arquivos"
        ),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
    ]

    settings_panels = PageSitePadrao.settings_panels + [
        FieldPanel("sensivel_periodo_eleitoral"),
    ]

    migracao_panels = [FieldPanel("body_migrated")]

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('descricao'),
    ]

    @staticmethod
    def get_arquivo_icon(arquivo):
        """Retorna o ícone correspondente ao tipo de arquivo."""
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    def get_context(self, request):
        """Adiciona arquivos com ícones ao contexto."""
        context = super().get_context(request)

        # Prepara uma lista de arquivos com seus ícones para o template
        arquivos_com_icone = []
        if self.arquivos:
            for block in self.arquivos:
                doc = block.value
                if doc:
                    arquivos_com_icone.append({
                        'documento': doc,
                        'icon_class': self.get_arquivo_icon(doc)
                    })
        context['arquivos_com_icone'] = arquivos_com_icone
        return context

    class Meta:
        abstract = True


# ============================================================
#                   CORPO TÉCNICO
# ============================================================

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

# Página genérica para uso em qualquer lugar do site
class RichTextPage(PageSitePadrao):
    """
    Página que permite a criação de conteúdo rico usando StreamField.
    Herda de PageSitePadrao para manter a consistência com o restante do site.
    """
    template = 'paginas/rich_text_page.html'
    
    # Defina os tipos de páginas que podem ser pais desta página
    parent_page_types = ['home.HomePage']  # Ajuste conforme necessário para sua estrutura
    
    # Campos do modelo
    body = StreamField(
        BaseStreamBlock(),  # Usa o BaseStreamBlock que já existe no seu projeto
        verbose_name="Conteúdo",
        use_json_field=True,
        blank=True,
        null=True,
        help_text="Adicione o conteúdo da página utilizando os blocos disponíveis."
    )
    
    # Painéis de conteúdo que aparecerão no admin do Wagtail
    content_panels = PageSitePadrao.content_panels + [
        FieldPanel('body'),
    ]
    
    # Configurações adicionais, os nomes que aparecerão no admin
    class Meta:
        verbose_name = "Página de Texto Rico"
        verbose_name_plural = "Páginas de Texto Rico"


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
