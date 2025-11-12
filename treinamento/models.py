from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin

from core.models import PageSitePadraoIndex
from blocks.models import (
    BannerComLinkBlock,
    AcessosRapidosBlock,
    NoticiasListBlock,
    TituloBlock,
    AvisosListBlock,
    CursosDestaquesBlock,
)


class TreinamentoIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    """
    Página índice de Treinamento.
    Herda de PageSitePadraoIndex e adiciona blocos customizados no body.
    """

    introduction = models.TextField(
        help_text="Texto introdutório para a página de treinamento",
        blank=True,
        default="Bem-vindo ao portal de treinamento"
    )

    body = StreamField(
        [
            ("banner", BannerComLinkBlock()),
            ("acesso_rapido", AcessosRapidosBlock()),
            ("noticias", NoticiasListBlock()),
            ("avisos", AvisosListBlock()),
            ("cursos_destaques", CursosDestaquesBlock()),
            ("titulo", TituloBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Adicione blocos de conteúdo para a página"
    )

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
    ]

    parent_page_types = [
        "home.HomePage",
        "intranet.IntranetHomePage",
    ]

    subpage_types = ["cursos.CursosIndexPage"]

    class Meta:
        verbose_name = "Página Índice de Treinamento"
        verbose_name_plural = "Páginas Índice de Treinamento"

    def get_context(self, request):
        """Adiciona cursos ao contexto."""
        context = super().get_context(request)
        
        # Busca cursos de páginas CursosIndexPage filhas
        from cursos.models import CursosPage
        cursos = CursosPage.objects.descendant_of(self).live().order_by("-data_publicacao")
        
        context["cursos"] = cursos
        
        return context

