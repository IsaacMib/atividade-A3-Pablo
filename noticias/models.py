from django.db import models
from django.core.exceptions import ValidationError

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
from wagtail.images.blocks import ImageChooserBlock
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter
)

MAX_NOTICIAS_DESTAQUE = 6


class NoticiasPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the NoticiasPage object and tags. There's a longer guide on using it at
    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

    content_object = ParentalKey(
        "NoticiasPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class NoticiasPage(PageSitePadrao):
    """
    Página que representa uma notícia.
    """
    subtitle = models.TextField(
        verbose_name="Subtítulo", blank=True, max_length=211)
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=False,
        help_text="Breve descrição do conteúdo da página.",
        max_length=211,
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação da notícia", default=datetime.now, blank=True, null=True
    )
    tags = ClusterTaggableManager(through=NoticiasPageTag, blank=True)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, null=True, use_json_field=True
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
        verbose_name="Notícia sensível ao período eleitoral",
        default=False,
        help_text="Marque se esta notícia deve ser ocultada ou tratada de forma especial durante o período eleitoral."
    )

    images = StreamField(
        [
            ("imagem", ImageChooserBlock(required=True, label="Imagem da notícia")),
        ],
        verbose_name="Coleção de Imagens",
        blank=True,
        null=True,
        use_json_field=True,
    )

    arquivos = StreamField(
        [
            ("arquivo", EspecificDocumentChooserBlock(
                required=True, label="Arquivos")),
        ],
        verbose_name="Arquivos da notícia",
        blank=True,
        null=True,
        use_json_field=True,
    )

    slideshow_imagens = models.BooleanField(
        verbose_name="Ativar slideshow de imagens",
        default=False,
        help_text="Marque para exibir as imagens como slideshow na página da notícia.",
    )

    nao_exibir_lista_de_arquivos = models.BooleanField(
        verbose_name="Não exibir lista de arquivos",
        default=False,
        help_text="Marque para não exibir a lista de arquivos na página da notícia.",
    )

    destaque = models.BooleanField(
        verbose_name="Notícia em destaque",
        default=False,
        help_text="Marque se esta notícia deve ser exibida em destaque na página inicial ou em listas de notícias. Só pode ser cadastrado 6 noticias  em destaque.",
    )

    # Painéis padrão
    content_panels = get_page_title_with_counter() + [
        FieldPanel("destaque"),
        FieldPanel("subtitle"),
        FieldPanel(
            "descricao",
            widget=get_widget_input_with_counter(char_limit=220)),
        MultiFieldPanel(
            [
                FieldPanel("slideshow_imagens"),
                FieldPanel("images"),
            ],
            heading="Imagens da notícia",
        ),
        MultiFieldPanel(
            [
                FieldPanel("nao_exibir_lista_de_arquivos"),
                FieldPanel("arquivos"),
            ],
            heading="Arquivos da notícia",
        ),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
    ]

    # Painel de promoções
    promote_panels = PageSitePadrao.promote_panels

    # Painel para campos migrados
    migracao_panels = [
        FieldPanel("body_migrated"),
    ]

    settings_panels = PageSitePadrao.settings_panels + [
        FieldPanel("sensivel_periodo_eleitoral"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Conteúdo"),
            # Adicionado painel de promoções
            ObjectList(promote_panels, heading="Promoções"),
            ObjectList(settings_panels, heading="Configurações"),
            ObjectList(migracao_panels, heading="Migração",
                       classname="migracao-only"),
        ]
    )

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access NoticiasPage objects with that tag
        """
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags

    # Specifies parent to NoticiasPage as being NoticiasIndexPages
    parent_page_types = ["NoticiasIndexPages"]

    # Specifies what content types can exist as children of NoticiasPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []

    def get_ultimas_noticias(self, quantidade=6):
        # Busca notícias em destaque ordenadas por data de publicação
        noticias_destaque = NoticiasPage.objects.live().filter(
            destaque=True
        ).order_by("-data_publicacao")
        
        # Busca notícias que não estão em destaque ordenadas por data de publicação
        noticias_sem_destaque = NoticiasPage.objects.live().filter(
            destaque=False
        ).order_by("-data_publicacao")
        
        # Combina as listas: primeiro as em destaque, depois as sem destaque
        noticias_combinadas = list(noticias_destaque) + list(noticias_sem_destaque)
        
        # Retorna apenas a quantidade solicitada
        return noticias_combinadas[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimas_noticias"] = self.get_ultimas_noticias()

        return context

    def get_imagem_destaque(self):
        """
        Retorna a primeira imagem da coleção de imagens (images) ou None se não houver.
        """
        if self.images and len(self.images):
            # Cada item é um bloco do tipo 'imagem'
            for bloco in self.images:
                if bloco.block_type == 'imagem' and bloco.value:
                    return bloco.value
        return None

    @staticmethod
    def get_arquivo_icon(arquivo):
        """
        Retorna a classe do ícone FontAwesome de acordo com a extensão ou mimetype do arquivo.
        """
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    class Meta:
        permissions = [
            ("view_conteudo_migrado", "Pode ver conteúdo migrado (body_migrated)"),
        ]
        default_permissions = []

    def get_admin_tabs(self, request):
        """
        Retorna os painéis de edição, mostrando o painel de migração apenas para quem tem permissão.
        """
        tabs = [
            ObjectList(self.content_panels, heading='Conteúdo'),
            ObjectList(self.settings_panels, heading='Configurações'),
        ]
        user = getattr(request, 'user', None)
        if user and (user.is_superuser or user.has_perm('core.view_conteudo_migrado')):
            tabs.append(ObjectList(self.migracao_panels, heading='Migração'))
        return TabbedInterface(tabs)

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('subtitle'),
        index.SearchField('descricao'),
    ]

    def clean(self):
        super().clean()
        
        if self.destaque:
            # Contar quantas notícias estão marcadas como destaque (excluindo a atual se já existe)
            noticias_destaque = NoticiasPage.objects.filter(destaque=True).live()
            
            # Se estamos editando uma notícia existente, excluí-la da contagem
            if self.pk:
                noticias_destaque = noticias_destaque.exclude(pk=self.pk)
            
            # Verificar se já existem 6 notícias em destaque
            if noticias_destaque.count() >= MAX_NOTICIAS_DESTAQUE:
                raise ValidationError({
                    'destaque': f'Só podem existir até {MAX_NOTICIAS_DESTAQUE} notícias em destaque. '
                               'Desmarque o destaque de outra notícia antes de marcar esta.'
                })

    def get_admin_display_title(self):
        """
        Adiciona asterisco (*) no título quando a notícia está em destaque
        """
        title = super().get_admin_display_title()
        if self.destaque:
            return f"★ {title}"
        return title


class NoticiasIndexPages(RoutablePageMixin, PageSitePadraoIndex):

    introduction = models.TextField(
        help_text="Texto para o topo da notícia",
        blank=False,
        default="Todas as Notícias")

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
    ]

    parent_page_types = [
        "home.HomePage",
    ]

    # Specifies that only NoticiasPage objects can live under this index page
    subpage_types = ["NoticiasPage"]

    # Defines a method to access the children of the page (e.g. NoticiasPage
    # objects). On the demo site we use this on the HomePage
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(NoticiasIndexPages, self).get_context(request)
        all_posts = NoticiasPage.objects.descendant_of(
            self).live().order_by("-data_publicacao")
        paginator = Paginator(all_posts, 12)  # Show 12 posts per page
        page = request.GET.get("page")
        try:
            # If the page exists and the ?page=x is an int
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If the ?page=x is not an int; show the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If the ?page=x is out of range (too high most likely)
            # Then return the last page
            posts = paginator.page(paginator.num_pages)
        context["posts"] = posts
        return context

     # This defines a Custom view that utilizes Tags. This view will return all
    # related NoticiasPage for a given Tag or redirect back to the BlogIndexPage.
    # More information on RoutablePages is at
    # https://docs.wagtail.org/en/stable/reference/contrib/routablepage.html
    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):

        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no blog posts tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {"self": self, "tag": tag, "posts": posts}
        return render(request, "noticias/noticias_index_pages.html", context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child NoticiasPage objects for this NoticiasIndexPages.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = NoticiasPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    # Returns the list of Tags for all child posts of this NoticiasPage.
    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            # Not tags.append() because we don't want a list of lists
            tags += post.get_tags
        tags = sorted(set(tags))
        return tags

    def get_ultimas_noticias(self, quantidade=6):
        # Busca notícias em destaque ordenadas por data de publicação
        noticias_destaque = NoticiasPage.objects.live().descendant_of(self).filter(
            destaque=True
        ).order_by("-data_publicacao")
        
        # Busca notícias que não estão em destaque ordenadas por data de publicação
        noticias_sem_destaque = NoticiasPage.objects.live().descendant_of(self).filter(
            destaque=False
        ).order_by("-data_publicacao")
        
        # Combina as listas: primeiro as em destaque, depois as sem destaque
        noticias_combinadas = list(noticias_destaque) + list(noticias_sem_destaque)
        
        # Retorna apenas a quantidade solicitada
        return noticias_combinadas[:quantidade]
    
        # return NoticiasPage.objects.live().descendant_of(self).order_by('-data_publicacao')[:quantidade]
