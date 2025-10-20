from django.forms import Textarea
from django.db import models
from django.urls import reverse
from wagtail.models import Page
from django.utils.text import slugify
from django.contrib import messages
from django.shortcuts import redirect, render
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
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
from core.models import SiteSettings
from django.core.exceptions import ValidationError


# ==========================================================
#  TAGS
# ==========================================================

class CursosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "CursosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


# ==========================================================
#  PÁGINA INDIVIDUAL DE CURSO
# ==========================================================

class CursosPage(PageSitePadrao):
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=False,
        help_text="Breve descrição do curso.",
        max_length=255
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do curso", default=datetime.now, blank=True, null=True
    )
    tags = ClusterTaggableManager(through=CursosPageTag, blank=True)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Conteúdo do curso", blank=True, null=True, use_json_field=True
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
    destaque = models.BooleanField(
        verbose_name="Exibir em Destaques",
        default=False,
        help_text="Marcar este curso como destaque?"
    )
    arquivos = StreamField(
        [
            ('arquivo', EspecificDocumentChooserBlock(
                required=True, label="Arquivos do curso")),
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

    content_panels = get_page_title_with_counter(50) + [
        FieldPanel("subtitle"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        FieldPanel('destaque'),
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

    promote_panels = PageSitePadrao.promote_panels
    migracao_panels = [FieldPanel("body_migrated")]
    settings_panels = PageSitePadrao.settings_panels

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(promote_panels, heading="Promoções"),
        ObjectList(settings_panels, heading='Configurações'),
        ObjectList(migracao_panels, heading='Migração', classname="migracao-only"),
    ])

    def get_absolute_url(self):
        return reverse("curso_detail", args=[str(self.id)])

    def generate_unique_slug(self, base_slug):
        slug = base_slug
        counter = 1
        parent = self.get_parent()
        parent_path = parent.path if parent else ''
        while CursosPage.objects.filter(slug=slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
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
            raise ValidationError({"title": "O título não pode ter mais que 50 caracteres."})
        if CursosPage.objects.filter(slug=self.slug, path__startswith=parent_path).exclude(pk=self.pk).exists():
            raise ValidationError("Esse título já está sendo usado em outro curso.")

    @property
    def get_tags(self):
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags

    parent_page_types = ["CursosIndexPage"]
    subpage_types = []

    def get_ultimos_cursos(self, quantidade=6):
        return CursosPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimos_cursos"] = self.get_ultimos_cursos()

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

        # URL absoluta da página (para os links de compartilhamento)
        absolute_url = request.build_absolute_uri(self.url)
        site_settings = SiteSettings.for_request(request)

        # Se o compartilhamento estiver habilitado, gera as redes
        redes_ativas = []
        if site_settings and site_settings.compartilhar_redes_sociais:
            redes_ativas = site_settings.get_redes_ativas(
                absolute_url=absolute_url,
                page_title=self.title
            )

        context["redes_ativas"] = redes_ativas
        context["compartilhar_redes_sociais"] = site_settings.compartilhar_redes_sociais if site_settings else False

        return context

    @staticmethod
    def get_arquivo_icon(arquivo):
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    class Meta:
        verbose_name = "Página de Curso"
        verbose_name_plural = "Páginas de Cursos"

    icon = "book"

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('subtitle'),
        index.SearchField('descricao'),
    ]


# ==========================================================
#  PÁGINA ÍNDICE DE CURSOS
# ==========================================================

class CursosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    introduction = models.TextField(
        help_text="Texto para o topo da página de cursos", blank=True
    )
    mostrar_destaque_primeiro = models.BooleanField(
        default=True,
        help_text="Marcar para exibir os cursos em destaque primeiro."
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("mostrar_destaque_primeiro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["CursosPage"]

    def get_posts_queryset(self, tag=None, somente_destaques=None):
        qs = CursosPage.objects.live().descendant_of(self)
        if somente_destaques is True:
            qs = qs.filter(destaque=True)
        elif somente_destaques is False:
            qs = qs.filter(destaque=False)
        if tag:
            qs = qs.filter(tags=tag)
        return qs.order_by("-data_publicacao")

    def paginate_queryset(self, request, queryset, per_page=12):
        paginator = Paginator(queryset, per_page)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_cursos_destaque(self, quantidade=6):
        destaques = list(self.get_posts_queryset(somente_destaques=True)[:quantidade])
        if len(destaques) < quantidade:
            faltam = quantidade - len(destaques)
            extras = list(
                self.get_posts_queryset(somente_destaques=False)
                .exclude(id__in=[a.id for a in destaques])[:faltam]
            )
            destaques += extras
        return destaques

    def get_ultimos_cursos(self, quantidade=6):
        return list(self.get_posts_queryset(somente_destaques=False)[:quantidade])

    def get_context(self, request):
        context = super().get_context(request)
        all_qs = self.get_posts_queryset()
        if self.mostrar_destaque_primeiro:
            all_list = sorted(
                list(all_qs),
                key=lambda p: (not p.destaque, -p.data_publicacao.toordinal() if p.data_publicacao else 0)
            )
            posts_page = self.paginate_queryset(request, all_list, per_page=12)
        else:
            posts_page = self.paginate_queryset(request, all_qs, per_page=12)

        context["posts"] = posts_page
        context["tag"] = None
        context["mostrar_destaque_primeiro"] = self.mostrar_destaque_primeiro
        return context

    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        tag_obj = None
        if tag:
            try:
                tag_obj = Tag.objects.get(slug=tag)
            except Tag.DoesNotExist:
                messages.add_message(request, messages.INFO, f'Não há cursos com a tag "{tag}"')
                return redirect(self.url)

        posts_qs = self.get_posts_queryset(tag=tag_obj)
        posts_page = self.paginate_queryset(request, posts_qs, per_page=12)

        context = super().get_context(request)
        context["posts"] = posts_page
        context["tag"] = tag_obj
        return render(request, "cursos/cursos_index_page.html", context)

    class Meta:
        verbose_name = "Página de Índice de Cursos"

    icon = "book-open"
