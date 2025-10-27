from django import forms
from django.db import models
from django.core.exceptions import ValidationError
import requests

from django.contrib import messages
from django.shortcuts import redirect, render
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.api import APIField
from wagtail.models import Page, Site
from core.models import PageSitePadrao, PageSitePadraoIndex

from blocks.models import BaseStreamBlock, EspecificDocumentChooserBlock
from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.api.fields import ImageRenditionField
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter
)

from core.models import ApiSettings


class NoticiaRemota:
    is_remote = True 

    def __init__(self, data, api_base_url):
        self.id = data.get('id')
        self.title = data.get('title', 'Sem título')
        self.subtitle = data.get('subtitle', '')
        self.descricao = data.get('descricao', '')
        self.destaque = data.get('destaque', False)
        self.body = data.get('body', '')
        self.imagem_destaque_remota = data.get('imagem_destaque')
        self.arquivos = data.get('arquivos', [])
        self.images = data.get('images', [])
        self.tags = data.get('tags', [])  # Adiciona as tags
        data_str = data.get('data_publicacao')
        if data_str:
            try:
                self.data_publicacao = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                self.data_publicacao = datetime.now(datetime.timezone.utc)
        else:
            self.data_publicacao = datetime.now(datetime.timezone.utc)

    @property
    def url(self):
        return f"/noticias/v1/{self.id}/"

    def get_imagem_destaque(self):
        return self.imagem_destaque_remota

    def get_tags(self):
        """
        Simula o comportamento do get_tags para notícias remotas.
        As tags vêm como uma lista de strings.
        """
        # Como não temos um 'slug' ou uma página de índice de tags para remotas,
        # não podemos gerar uma URL funcional por enquanto.
        # Retornamos uma lista de objetos simples para exibição.
        return [{'name': tag, 'url': '#'} for tag in self.tags]




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
        BaseStreamBlock(), verbose_name="Corpo da Página", blank=True, null=True, use_json_field=True
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

    # Campos expostos na API
    api_fields = [
        APIField('title'),
        APIField('subtitle'),
        APIField('descricao'),
        APIField('data_publicacao'),
        APIField('body'),
        APIField('tags'),
        # Usamos 'get_imagem_destaque' para garantir que pegamos a imagem correta
        APIField('get_imagem_destaque', serializer=ImageRenditionField('fill-800x450', source='get_imagem_destaque')),
        APIField('url'),
    ]

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
        noticias_destaque = NoticiasPage.objects.live().filter(
            destaque=True
        ).order_by("-data_publicacao")
        
        noticias_sem_destaque = NoticiasPage.objects.live().filter(
            destaque=False
        ).order_by("-data_publicacao")
        
        noticias_combinadas = list(noticias_destaque) + list(noticias_sem_destaque)
        
        return noticias_combinadas[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        noticias_index = NoticiasIndexPages.objects.live().first()
        if noticias_index:
            context["ultimas_noticias"] = noticias_index.get_ultimas_noticias()
        else:
            context["ultimas_noticias"] = self.get_ultimas_noticias() # Fallback para o método antigo
        return context

    def get_imagem_destaque(self):
        if self.images and len(self.images):
            for bloco in self.images:
                if bloco.block_type == 'imagem' and bloco.value:
                    return bloco.value
        return None

    @staticmethod
    def get_arquivo_icon(arquivo):

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
        context = super().get_context(request)
        
        # 1. Busca as notícias locais
        noticias_locais = list(NoticiasPage.objects.descendant_of(
            self).live().order_by("-data_publicacao")
        )

        # 2. Busca notícias da API externa
        noticias_remotas = self._fetch_remote_noticias()

        # 3. Combina e ordena as listas
        all_posts = sorted(
            noticias_locais + noticias_remotas,
            key=lambda x: x.data_publicacao,
            reverse=True
        )

        # 4. Paginação
        paginator = Paginator(all_posts, 12)
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context["posts"] = posts
        return context

    def _fetch_remote_noticias(self):
        """
        Busca notícias de uma API externa com base nas configurações do site.
        """
        try:
            site = Site.objects.get(is_default_site=True)
            api_settings = ApiSettings.for_site(site)
        except (Site.DoesNotExist, ApiSettings.DoesNotExist):
            return []

        if not api_settings.api_habilitada or not api_settings.puxar_noticias:
            return []

        # Obter token
        token_url = f"{api_settings.api_url.rstrip('/')}/api/v1/get-token/"
        try:
            response = requests.post(
                token_url,
                data={'username': api_settings.api_usuario, 'password': api_settings.api_senha},
                timeout=10
            )
            response.raise_for_status()
            token = response.json().get('token')
            if not token:
                return []
            auth_token = f"Token {token}"
        except requests.RequestException:
            return [] 
        base_api_url = f"{api_settings.api_url.rstrip('/')}/api/v1/shared-content"
        tags_noticias = [tag.strip() for tag in api_settings.tags_noticias.split(',') if tag.strip()]
        headers = {'Authorization': auth_token}
        remote_data = []
        seen_ids = set()

        if tags_noticias:
            for tag_slug in tags_noticias:
                noticias_url = f"{base_api_url}/tag/{tag_slug}/?noticias=true"
                try:
                    response = requests.get(noticias_url, headers=headers, timeout=15)
                    response.raise_for_status()
                    items = response.json()
                    for item in items:
                        if item.get('id') not in seen_ids:
                            remote_data.append(item)
                            seen_ids.add(item.get('id'))
                except requests.RequestException:
                    continue
        else:
            noticias_url = f"{base_api_url}/all/?noticias=true"
            try:
                response = requests.get(noticias_url, headers=headers, timeout=15)
                response.raise_for_status()
                remote_data = response.json()
            except requests.RequestException:
                return []

        noticias_remotas = []
        for item in remote_data:
            noticias_remotas.append(NoticiaRemota(item, api_base_url=api_settings.api_url))
            
        return noticias_remotas

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

        noticias_locais = list(NoticiasPage.objects.live().descendant_of(self).order_by("-data_publicacao"))

        noticias_remotas = self._fetch_remote_noticias()

        all_posts = sorted(
            noticias_locais + noticias_remotas,
            key=lambda x: x.data_publicacao,
            reverse=True
        )
        
        # 4. Retorna a quantidade solicitada
        return all_posts[:quantidade]
    
        # return NoticiasPage.objects.live().descendant_of(self).order_by('-data_publicacao')[:quantidade]
