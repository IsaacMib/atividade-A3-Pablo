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


class EventosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "EventosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class EventosPage(PageSitePadrao):
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255)
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=False,
        help_text="Breve descrição do conteúdo da página.",
        max_length=255
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do evento", default=datetime.now, blank=True, null=True)
    tags = ClusterTaggableManager(through=EventosPageTag, blank=True)
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
        verbose_name="Evento sensível ao período eleitoral",
        default=False,
        help_text="Marque se este evento deve ser ocultado ou tratado de forma especial durante o período eleitoral."
    )
    arquivos = StreamField(
        [
            ('arquivo', EspecificDocumentChooserBlock(
                required=True, label="Arquivos")),
        ],
        verbose_name="Arquivos do evento",
        blank=True,
        null=True,
        use_json_field=True,
    )
    nao_exibir_lista_de_arquivos = models.BooleanField(
        verbose_name="Não exibir lista de arquivos",
        default=False,
        help_text="Marque para não exibir a lista de arquivos na página do evento."
    )

    content_panels = get_page_title_with_counter(50) + [
        FieldPanel("subtitle"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        MultiFieldPanel(
            [
                FieldPanel("nao_exibir_lista_de_arquivos"),
                FieldPanel("arquivos"),
            ],
            heading="Arquivos do evento"
        ),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
    ]

    promote_panels = PageSitePadrao.promote_panels

    migracao_panels = [
        FieldPanel("body_migrated"),
    ]

    settings_panels = PageSitePadrao.settings_panels + [
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
        while EventosPage.objects.filter(slug=slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
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
        if len(self.title) > 50:
            raise ValidationError(
                {"title": "O título não pode ter mais que 50 caracteres."})

        if EventosPage.objects.filter(slug=self.slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
            raise ValidationError(
                "Esse título já está sendo usado em outro evento.")

    @property
    def get_tags(self):
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags

    parent_page_types = ["EventosIndexPage"]
    subpage_types = []

    def get_ultimos_eventos(self, quantidade=6):
        return EventosPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimos_eventos"] = self.get_ultimos_eventos()

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
        verbose_name = "Página de Evento"
        verbose_name_plural = "Páginas de Eventos"

    icon = "calendar"

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('subtitle'),
        index.SearchField('descricao'),
    ]


class EventosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    introduction = models.TextField(
        help_text="Texto para o topo da página de eventos", blank=True)    
   

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["EventosPage"]

    def get_context(self, request):
        context = super(EventosIndexPage, self).get_context(request)
        all_posts = EventosPage.objects.descendant_of(
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
        context["tag"] = None
        return context

    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        try:
            tag_obj = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = f'Não há eventos com a tag "{tag}"'
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag_obj)
        context = self.get_context(request)
        context["tag"] = tag_obj
        context["posts"] = posts
        return render(request, "eventos/eventos_index_page.html", context)

    def get_posts(self, tag=None):
        posts = EventosPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    def get_ultimos_eventos(self, quantidade=6):
        return EventosPage.objects.live().descendant_of(self).order_by('-data_publicacao')[:quantidade]

    class Meta:
        verbose_name = "Página de Índice de Eventos"

    icon = "list-ul"
