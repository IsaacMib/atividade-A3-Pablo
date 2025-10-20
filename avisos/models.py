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
from wagtail.contrib.settings.models import BaseSiteSetting
from django.utils.html import escape
from wagtail.admin.panels import ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
from wagtail.fields import StreamField
from wagtail.search import index

from core.models import PageSitePadrao, PageSitePadraoIndex, SiteSettings
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


class AvisosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "AvisosPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class AvisosPage(PageSitePadrao):
    subtitle = models.CharField(
        verbose_name="Subtítulo", blank=True, max_length=255)
    descricao = models.TextField(
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
    destaque = models.BooleanField(

        verbose_name="Exibir em Destaques",
        default=False,
        help_text="Marcar este aviso como destaque?"
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

    content_panels = get_page_title_with_counter(50) + [
        FieldPanel("subtitle"),
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        FieldPanel('destaque'),
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

    parent_page_types = ["AvisosIndexPage"]
    subpage_types = []
    icon = "warning"

    search_fields = PageSitePadrao.search_fields + [
            
            index.SearchField('body'),
            index.SearchField('subtitle'),
            index.SearchField('descricao'),
            ]


    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        

    def get_absolute_url(self):
        return reverse("aviso_detail", args=[str(self.id)])


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
        if len(self.title) > 50:
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

    @staticmethod
    def get_arquivo_icon(arquivo):
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    def get_ultimos_avisos(self, quantidade=6):
        return AvisosPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimos_avisos"] = self.get_ultimos_avisos()

        return context
    
    def get_context(self, request):
        context = super().get_context(request)

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

        # Adiciona ao contexto
        context["redes_ativas"] = redes_ativas
        context["compartilhar_redes_sociais"] = site_settings.compartilhar_redes_sociais

        return context



    
class AvisosIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    introduction = models.TextField(
        help_text="Texto para o topo da página de avisos", blank=True
    )

    mostrar_destaque_primeiro = models.BooleanField(
        default=True,
        help_text="Marcar para exibir os avisos em destaque primeiro."
    )

    parent_page_types = ["home.HomePage"]
    subpage_types = ["AvisosPage"]
    icon = "list-ul"

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("mostrar_destaque_primeiro"),
    ]

    def get_posts_queryset(self, tag=None, somente_destaques=None):

        qs = AvisosPage.objects.live().descendant_of(self)

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
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_avisos_destaque(self, quantidade=6):

        destaques = list(
            self.get_posts_queryset(somente_destaques=True)[:quantidade]
        )
        if len(destaques) < quantidade:
            faltam = quantidade - len(destaques)
            extras = list(
                self.get_posts_queryset(somente_destaques=False)
                .exclude(id__in=[a.id for a in destaques])[:faltam]
            )
            destaques += extras
        return destaques
    
    def get_ultimos_avisos(self, quantidade=6):

        return list(self.get_posts_queryset(somente_destaques=False)[:quantidade])

    def get_context(self, request):
        context = super().get_context(request)
        all_qs = self.get_posts_queryset()

        if self.mostrar_destaque_primeiro:
            all_list = list(all_qs)
            all_list = sorted(
                all_list,
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
                messages.add_message(request, messages.INFO, f'Não há avisos com a tag "{tag}"')
                return redirect(self.url)

        posts_qs = self.get_posts_queryset(tag=tag_obj)
        posts_page = self.paginate_queryset(request, posts_qs, per_page=12)

        context = super().get_context(request)
        context["posts"] = posts_page
        context["tag"] = tag_obj
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
