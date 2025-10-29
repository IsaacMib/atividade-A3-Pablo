from django.forms import Textarea
from django.db import models
from wagtail.models import Page
from django.utils.text import slugify
from django.contrib import messages
from django.shortcuts import redirect, render
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
from wagtail.fields import StreamField
from wagtail.search import index
from core.models import PageSitePadrao, PageSitePadraoIndex
from blocks.models import BaseStreamBlock, EspecificDocumentChooserBlock
from datetime import datetime
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter
)
from django.core.exceptions import ValidationError
from wagtail.images.blocks import ImageChooserBlock


class CursosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "CursosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class CursosPage(PageSitePadrao):
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=False,
        help_text="Breve descrição do conteúdo da página.",
        max_length=255
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do curso", default=datetime.now, blank=True, null=True)
    tags = ClusterTaggableManager(through=CursosPageTag, blank=True)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Corpo da página", blank=True, null=True, use_json_field=True
    )
    body_migrated = models.TextField(
        help_text="Usado apenas para conteúdo do antigo site Plone.",
        null=True,
        blank=True
    )
    plone_node_id = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        unique=True,
        help_text="ID do nó no Plone, usado para identificar a página migrada."
    )

    images = StreamField(
        [("imagem", ImageChooserBlock(required=True, label="Imagem do curso"))],
        verbose_name="Coleção de Imagens",
        blank=True,
        null=True,
        use_json_field=True,
    )

    arquivos = StreamField(
        [
            ('arquivo', EspecificDocumentChooserBlock(
                required=True, label="Arquivos")),
        ],
        verbose_name="Arquivos do curso",
        blank=True,
        null=True,
        use_json_field=True,
    )

    nao_exibir_lista_de_arquivos = models.BooleanField(
        verbose_name="Não exibir lista de arquivos",
        default=False,
        help_text="Marque para não exibir a lista de arquivos na página do curso."
    )

    destaque = models.BooleanField(
        "Curso em destaque",
        default=False,
        help_text="Exibe o curso em destaque na página inicial. Máximo de 6 cursos."
    )

    content_panels = get_page_title_with_counter(100) + [
        FieldPanel("destaque"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        MultiFieldPanel(
            [
                FieldPanel("nao_exibir_lista_de_arquivos"),
                FieldPanel("arquivos"),
            ],
            heading="Arquivos do curso"
        ),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
    ]

    # Painel de promoções
    promote_panels = PageSitePadrao.promote_panels

    migracao_panels = [
        FieldPanel("body_migrated"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(promote_panels, heading="Promoções"),
        ObjectList(migracao_panels, heading='Migração',
                   classname="migracao-only"),
    ])

    parent_page_types = ["CursosIndexPage"]
    subpage_types = []

    def clean(self):
        super().clean()
        parent = self.get_parent()
        parent_path = parent.path if parent else ''
        if len(self.title) > 100:
            raise ValidationError(
                {"title": "O título não pode ter mais que 100 caracteres."})

        if CursosPage.objects.filter(slug=self.slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
            raise ValidationError(
                "Esse título já está sendo usado em outro curso.")

    @property
    def get_tags(self):
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags

    def get_ultimos_cursos(self, quantidade=6):
        return CursosPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimos_cursos"] = self.get_ultimos_cursos()

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
        """Exibe ícone ★ ao lado do título se o curso for destaque."""
        title = super().get_admin_display_title()
        return f"★ {title}" if self.destaque else title

    class Meta:
        verbose_name = "Página de Curso"
        verbose_name_plural = "Páginas de Cursos"
        permissions = [("view_conteudo_migrado", "Pode ver conteúdo migrado (body_migrated)")]
        default_permissions = []

    icon = "warning"

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('descricao'),
    ]


class CursosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    introduction = models.TextField(
        help_text="Texto para o topo da página de cursos", blank=True)

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["CursosPage"]

    def get_context(self, request):
        context = super(CursosIndexPage, self).get_context(request)
        all_posts = CursosPage.objects.descendant_of(
            self).live().order_by("-data_publicacao")
        paginator = Paginator(all_posts, 12)
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context["posts"] = posts
        context["tag"] = None  # Garante que a variável tag exista no contexto
        return context

    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        try:
            tag_obj = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = f'Não há cursos com a tag "{tag}"'
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag_obj)
        context = self.get_context(request)
        context["tag"] = tag_obj
        context["posts"] = posts
        return render(request, "cursos/cursos_index_page.html", context)

    def get_posts(self, tag=None):
        posts = CursosPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    def get_ultimos_cursos(self, quantidade=6):
        """Retorna os cursos em destaque e recentes do índice."""
        destaques = list(
            CursosPage.objects.live()
            .descendant_of(self)
            .filter(destaque=True)
            .order_by("-data_publicacao")[:quantidade]
        )
        if len(destaques) >= quantidade:
            return destaques
        
        falta = quantidade - len(destaques)

        restantes = (
            CursosPage.objects.live()
            .descendant_of(self)
            .filter(destaque=False)
            .order_by("-data_publicacao")[:falta]
        )
        return destaques + list(restantes)

    class Meta:
        verbose_name = "Página de Índice de Cursos"

    icon = "book-open"
