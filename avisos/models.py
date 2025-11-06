from datetime import datetime
from django.db import models
from wagtail.models import Page
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import (
    ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseSiteSetting

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from core.models import PageSitePadrao, PageSitePadraoIndex, SiteSettings
from blocks.models import BaseStreamBlock, EspecificDocumentChooserBlock
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter
)
from django.core.exceptions import ValidationError
from wagtail.images.blocks import ImageChooserBlock

MAX_AVISOS_DESTAQUE = 6


# ============================================================
#                       MODELO DE TAG
# ============================================================

class AvisosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "AvisosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


# ============================================================
#                       MODELO DE AVISO
# ============================================================

class AvisosPage(PageSitePadrao):
    descricao = models.TextField(
        "Descrição",
        help_text="Breve descrição do conteúdo da página.",
        max_length=255
    )

    data_publicacao = models.DateTimeField(
        "Data de publicação do aviso",
        default=datetime.now,
        blank=True,
        null=True
    )

    resumo = models.TextField(
        "Resumo automático",
        blank=True,
        help_text="Gerado automaticamente a partir do corpo ou descrição (120 caracteres)."
    )

    tags = ClusterTaggableManager(through=AvisosPageTag, blank=True)

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
        "Aviso sensível ao período eleitoral",
        default=False,
        help_text="Marque se este aviso deve ser ocultado durante o período eleitoral."
    )

    images = StreamField(
        [("imagem", ImageChooserBlock(required=True, label="Imagem do aviso"))],
        verbose_name="Coleção de Imagens",
        blank=True,
        null=True,
        use_json_field=True,
    )

    slideshow_imagens = models.BooleanField(
        "Ativar slideshow de imagens",
        default=False,
        help_text="Exibir as imagens como slideshow na página do aviso.",
    )

    arquivos = StreamField(
        [("arquivo", EspecificDocumentChooserBlock(required=True, label="Arquivos"))],
        verbose_name="Arquivos do aviso",
        blank=True,
        null=True,
        use_json_field=True,
    )

    nao_exibir_lista_de_arquivos = models.BooleanField(
        "Não exibir lista de arquivos",
        default=False,
        help_text="Marque para ocultar a lista de arquivos.",
    )

    destaque = models.BooleanField(
        "Aviso em destaque",
        default=False,
        help_text="Exibe o aviso em destaque na página inicial. Máximo de 6 avisos."
    )

    content_panels = get_page_title_with_counter(100) + [
        FieldPanel("destaque"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        MultiFieldPanel(
            [FieldPanel("slideshow_imagens"), FieldPanel("images")],
            heading="Imagens do aviso"
        ),
        MultiFieldPanel(
            [
                FieldPanel("nao_exibir_lista_de_arquivos"),
                FieldPanel("arquivos"),
            ],
            heading="Arquivos do aviso"
        ),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
    ]

    promote_panels = PageSitePadrao.promote_panels

    settings_panels = PageSitePadrao.settings_panels + [
        FieldPanel("sensivel_periodo_eleitoral"),
    ]

    migracao_panels = [FieldPanel("body_migrated")]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Conteúdo"),
        ObjectList(promote_panels, heading="Promoções"),
        ObjectList(settings_panels, heading="Configurações"),
        ObjectList(migracao_panels, heading="Migração", classname="migracao-only"),
    ])

    parent_page_types = ["AvisosIndexPage"]
    subpage_types = []

    def clean(self):
        """Validação de limite de destaques."""
        super().clean()
        parent = self.get_parent()
        parent_path = parent.path if parent else ''
        if len(self.title) > 100:
            raise ValidationError(
                {"title": "O título não pode ter mais que 100 caracteres."})

    @staticmethod
    def get_arquivo_icon(arquivo):
        """Retorna o ícone correspondente ao tipo de arquivo."""
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    @property
    def get_tags(self):
        """Retorna as tags com suas URLs completas."""
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags
    
    def get_imagem_destaque(self):
        """Retorna a primeira imagem do bloco de imagens."""
        if self.images:
            for bloco in self.images:
                if bloco.block_type == "imagem" and bloco.value:
                    return bloco.value
        return None

    def get_ultimos_avisos(self, quantidade=6):
        """Retorna lista de avisos em destaque + recentes."""
        destaques = list(AvisosPage.objects.live().filter(destaque=True).order_by("-data_publicacao")[:quantidade])
        if len(destaques) >= quantidade:
            return destaques

        restantes = AvisosPage.objects.live().filter(destaque=False).order_by("-data_publicacao")[:quantidade - len(destaques)]
        return destaques + list(restantes)

    def get_context(self, request):
        """Adiciona avisos recentes e redes sociais ao contexto."""
        context = super().get_context(request)
        context["ultimos_avisos"] = self.get_ultimos_avisos()

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

    @staticmethod
    def get_arquivo_icon(arquivo):
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)
    
    def get_admin_display_title(self):
        """Exibe ícone ★ ao lado do título se o aviso for destaque."""
        title = super().get_admin_display_title()
        return f"★ {title}" if self.destaque else title

    class Meta:
        verbose_name = "Página de Aviso"
        verbose_name_plural = "Páginas de Avisos"
        permissions = [("view_conteudo_migrado", "Pode ver conteúdo migrado (body_migrated)")]
        default_permissions = []

    icon = "warning"

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('descricao'),
    ]


# ============================================================
#                     INDEX DE AVISOS
# ============================================================

class AvisosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    """Página de listagem dos avisos."""

    introduction = models.TextField(
        "Introdução",
        default="Todos os avisos",
        help_text="Texto exibido no topo da página de avisos.",
    )

    content_panels = PageSitePadraoIndex.content_panels + [FieldPanel("introduction")]

    parent_page_types = ["home.HomePage", "intranet.IntranetHomePage"]
    subpage_types = ["AvisosPage"]
    icon = "list-ul"

    def children(self):
        return self.get_children().specific().live()

    def get_posts(self, tag=None):
        posts = AvisosPage.objects.live().descendant_of(self)
        return posts.filter(tags=tag) if tag else posts

    def get_context(self, request):
        """Adiciona posts paginados ao contexto."""
        context = super().get_context(request)
        all_posts = AvisosPage.objects.descendant_of(self).live().order_by("-data_publicacao")
        paginator = Paginator(all_posts, 12)
        page = request.GET.get("page")

        try:
            posts = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            posts = paginator.page(1)

        context["posts"] = posts
        return context

    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        """Filtra avisos por tag."""
        try:
            tag_obj = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                messages.info(request, f'Não há avisos com a tag "{tag}".')
            return redirect(self.url)

        posts = self.get_posts(tag=tag_obj)
        return render(request, "avisos/avisos_index_pages.html", {
            "self": self,
            "tag": tag_obj,
            "posts": posts,
        })

    def get_ultimos_avisos(self, quantidade=6):
        """Retorna os avisos em destaque e recentes do índice."""
        destaques = list(
            AvisosPage.objects.live()
            .descendant_of(self)
            .filter(destaque=True)
            .order_by("-data_publicacao")[:quantidade]
        )
        if len(destaques) >= quantidade:
            return destaques
        
        falta = quantidade - len(destaques)

        restantes = (
            AvisosPage.objects.live()
            .descendant_of(self)
            .filter(destaque=False)
            .order_by("-data_publicacao")[:falta]
        )
        return destaques + list(restantes)

    class Meta:
        verbose_name = "Página de Índice de Avisos"

    icon = "list-ul"
