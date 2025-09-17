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
from wagtail.admin.panels import ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface, PanelPlaceholder
from wagtail.fields import StreamField
from wagtail.search import index
from core.models import Page as DefaultWagtailPage
from blocks.models import BaseStreamBlock, EspecificDocumentChooserBlock
from datetime import datetime
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from core.utils import get_file_type, get_fontawesome_file_icon
from django.core.exceptions import ValidationError
from django import forms

TITULO_MAX_LENGTH = 50


class AvisosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "AvisosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class Page(DefaultWagtailPage):

    class Meta:
        proxy = True

    content_panels = [
        PanelPlaceholder("wagtail.admin.panels.TitleFieldPanel", ["title"], {
            'widget': forms.TextInput(attrs={
                'data-controller': 'char-count',
                'data-char-count-max-value': TITULO_MAX_LENGTH,
                'data-action': 'input->char-count#updateCount paste->char-count#updateCount',
            }),
        }),
    ] + Page.content_panels[1:]


class AvisosPage(Page):
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255)
    descricao = models.CharField(
        verbose_name="Descrição",
        blank=False,
        help_text="Breve descrição do conteúdo da página.",
        max_length=255
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do aviso", default=datetime.now, blank=True, null=True)
    tags = ClusterTaggableManager(through=AvisosPageTag, blank=True)
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
    sensivel_periodo_eleitoral = models.BooleanField(
        verbose_name="Aviso sensível ao período eleitoral",
        default=False,
        help_text="Marque se este aviso deve ser ocultado ou tratado de forma especial durante o período eleitoral."
    )
    arquivos = StreamField(
        [
            ('arquivo', EspecificDocumentChooserBlock(
                required=True, label="Arquivos")),
        ],
        verbose_name="Arquivos do aviso",
        blank=True,
        null=True,
        use_json_field=True,
    )
    nao_exibir_lista_de_arquivos = models.BooleanField(
        verbose_name="Não exibir lista de arquivos",
        default=False,
        help_text="Marque para não exibir a lista de arquivos na página do aviso."
    )

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("descricao", widget=forms.Textarea(attrs={
            'data-controller': 'char-count',
            'data-char-count-max-value': 255,
            'data-action': 'input->char-count#updateCount paste->char-count#updateCount',
        })),
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

    # Painel de promoções
    promote_panels = Page.promote_panels

    migracao_panels = [
        FieldPanel("body_migrated"),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("sensivel_periodo_eleitoral"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(promote_panels, heading="Promoções"),
        ObjectList(settings_panels, heading='Configurações'),
        ObjectList(migracao_panels, heading='Migração',
                   classname="migracao-only"),
    ])

    def generate_unique_slug(self, base_slug):
        slug = base_slug
        counter = 1
        parent = self.get_parent()
        parent_path = parent.path if parent else ''
        while AvisosPage.objects.filter(slug=slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            self.slug = self.generate_unique_slug(base_slug)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        parent = self.get_parent()
        parent_path = parent.path if parent else ''
        if len(self.title) > TITULO_MAX_LENGTH:
            raise ValidationError(
                {"title": "O título não pode ter mais que 50 caracteres."})

        if AvisosPage.objects.filter(slug=self.slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
            raise ValidationError(
                "Esse título já está sendo usado em outro aviso.")

    @property
    def get_tags(self):
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags

    parent_page_types = ["AvisosIndexPage"]
    subpage_types = []

    def get_ultimos_avisos(self, quantidade=6):
        return AvisosPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
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

    class Meta:
        verbose_name = "Página de Aviso"
        verbose_name_plural = "Páginas de Avisos"

    icon = "warning"

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('subtitle'),
        index.SearchField('descricao'),
    ]


class AvisosIndexPage(RoutablePageMixin, Page):
    introduction = models.TextField(
        help_text="Texto para o topo da página de avisos", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["AvisosPage"]

    def get_context(self, request):
        context = super(AvisosIndexPage, self).get_context(request)
        all_posts = AvisosPage.objects.descendant_of(
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
                msg = f'Não há avisos com a tag "{tag}"'
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag_obj)
        context = self.get_context(request)
        context["tag"] = tag_obj
        context["posts"] = posts
        return render(request, "avisos/avisos_index_page.html", context)

    def get_posts(self, tag=None):
        posts = AvisosPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    def get_ultimos_avisos(self, quantidade=6):
        return AvisosPage.objects.live().descendant_of(self).order_by('-data_publicacao')[:quantidade]

    class Meta:
        verbose_name = "Página de Índice de Avisos"

    icon = "list-ul"
