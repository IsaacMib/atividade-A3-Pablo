from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from datetime import datetime
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib import messages
from django import forms


from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.search import index
from wagtail.documents.blocks import DocumentChooserBlock

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import PageSitePadrao, PageSitePadraoIndex
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter,
)

# ============================================================
# TAGS
# ============================================================
class DocumentosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "DocumentosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


# ============================================================
# PÁGINA INDIVIDUAL
# ============================================================
class DocumentosPage(PageSitePadrao):
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        help_text="Breve descrição do documento.",
        max_length=255,
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação", default=datetime.now, blank=True, null=True
    )
    tags = ClusterTaggableManager(through=DocumentosPageTag, blank=True)
    destaque = models.BooleanField(
        verbose_name="Documento importante (destaque)",
        default=False,
        help_text="Marque para exibir este documento na seção de Destaques.",
    )
    arquivo = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Arquivo",
    )

    content_panels = get_page_title_with_counter(50) + [
        FieldPanel("subtitle"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        FieldPanel("arquivo"),
        FieldPanel("destaque"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
    ]

    promote_panels = PageSitePadrao.promote_panels
    settings_panels = PageSitePadrao.settings_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Conteúdo"),
            ObjectList(promote_panels, heading="Promoções"),
            ObjectList(settings_panels, heading="Configurações"),
        ]
    )

    parent_page_types = ["DocumentosIndexPage"]
    subpage_types = []

    icon = "doc-full"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    def get_absolute_url(self):
        return reverse("documento_detail", args=[str(self.id)])

    def generate_unique_slug(self, base_slug):
        slug = base_slug
        counter = 1
        parent = self.get_parent()
        parent_path = parent.path if parent else ""
        while DocumentosPage.objects.filter(
            slug=slug, path__startswith=parent_path
        ).exclude(pk=self.pk).exists():
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
        if len(self.title) > 50:
            raise ValidationError(
                {"title": "O título não pode ter mais que 50 caracteres."}
            )

    @staticmethod
    def get_arquivo_icon(arquivo):
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    @property
    def get_tags(self):
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}?tag={tag.slug}"
        return tags


# ============================================================
# PÁGINA DE ÍNDICE DE DOCUMENTOS
# ============================================================
class DocumentosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    introduction = models.TextField(
        help_text="Texto para o topo da página de documentos", blank=True
    )
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255
    )
    mostrar_destaque_primeiro = models.BooleanField(
        default=True,
        help_text="Marcar para exibir os documentos em destaque primeiro.",
    )

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("mostrar_destaque_primeiro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["DocumentosPage"]
    icon = "folder-open-1"

    class Meta:
        verbose_name = "Página de Índice de Documentos"
        verbose_name_plural = "Páginas de Índice de Documentos"

    # ============================================================
    # LISTAGEM E FILTROS
    # ============================================================
    def get_posts_queryset(self, tag=None, somente_destaques=None):
        qs = DocumentosPage.objects.live().descendant_of(self)
        if somente_destaques is True:
            qs = qs.filter(destaque=True)
        elif somente_destaques is False:
            qs = qs.filter(destaque=False)
        if tag:
            qs = qs.filter(tags=tag)
        qs = qs.order_by("-data_publicacao")
        return qs

    def paginate_queryset(self, request, queryset, per_page=12):
        paginator = Paginator(queryset, per_page)
        page_number = request.GET.get("page")
        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def get_context(self, request):
        context = super().get_context(request)
        tag_slug = request.GET.get("tag")
        tag_obj = None
        if tag_slug:
            try:
                tag_obj = Tag.objects.get(slug=tag_slug)
            except Tag.DoesNotExist:
                messages.info(request, f'Não há documentos com a tag "{tag_slug}"')
                return redirect(self.url)

        qs = self.get_posts_queryset(tag=tag_obj)
        ano = request.GET.get("ano")
        if ano:
            qs = qs.filter(data_publicacao__year=ano)

        if self.mostrar_destaque_primeiro:
            all_list = sorted(
                qs,
                key=lambda p: (
                    not p.destaque,
                    -p.data_publicacao.toordinal() if p.data_publicacao else 0,
                ),
            )
        else:
            all_list = list(qs)

        posts_page = self.paginate_queryset(request, all_list, per_page=12)
        context["documentos"] = posts_page
        context["tag"] = tag_obj
        context["ano"] = ano
        context["tags"] = (
            Tag.objects.filter(documentos_documentospagetag_items__content_object__live=True)
            .distinct()
            .order_by("name")
            )

        context["anos_disponiveis"] = (
            DocumentosPage.objects.live()
            .dates("data_publicacao", "year", order="DESC")
        )
        return context
