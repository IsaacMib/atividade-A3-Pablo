from django.db import models
from django.utils.text import slugify
from django.contrib import messages
from django.shortcuts import redirect, render
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
from wagtail.search import index
from core.models import PageSitePadraoIndex
from paginas.models import AvisosDefaultPage
from datetime import datetime
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from core.utils import get_page_title_with_counter, get_widget_input_with_counter
from django.core.exceptions import ValidationError


class EventosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "EventosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class EventosPage(AvisosDefaultPage):
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255)

    tags = ClusterTaggableManager(through=EventosPageTag, blank=True)

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

    promote_panels = AvisosDefaultPage.promote_panels

    migracao_panels = [
        FieldPanel("body_migrated"),
    ]

    settings_panels = AvisosDefaultPage.settings_panels

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(promote_panels, heading="Promoções"),
        ObjectList(settings_panels, heading='Configurações'),
        ObjectList(migracao_panels, heading='Migração',
                   classname="migracao-only"),
    ])

    parent_page_types = ["EventosIndexPage"]
    subpage_types = []

    template = "paginas/avisos_default_page.html"

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

    def get_ultimos_eventos(self, quantidade=6):
        return EventosPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimos_eventos"] = self.get_ultimos_eventos()
        return context

    class Meta:
        verbose_name = "Página de Evento"
        verbose_name_plural = "Páginas de Eventos"

    icon = "calendar"

    search_fields = AvisosDefaultPage.search_fields + [
        index.SearchField('subtitle'),
    ]


class EventosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    introduction = models.TextField(
        help_text="Texto para o topo da página de eventos", blank=True)    
   
    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
    ]

    parent_page_types = ["home.HomePage", "intranet.IntranetHomePage"]
    subpage_types = ["EventosPage"]

    template = "paginas/avisos_default_index_page.html"

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
        return render(request, "paginas/avisos_default_index_page.html", context)

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
