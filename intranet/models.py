from django.db import models
from django.http import HttpResponseRedirect
from django.conf import settings
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.fields import StreamField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail import blocks
from blocks.agenda import ( 

    ListAgendaBlock, 
    CompromissoBlock, 
    AgendaDoDiaBlock,
)
from core.models import PageSitePadrao, PageSitePadraoIndex
    

from blocks.models import (

    AcessosRapidosBlock,
    BannerComLinkBlock,
    ListaVideosBlock,
    OdometerListBlock,
    CarrosselBannersBlock,
    ServicosOnlineBlock,
    TituloBlock,
    NoticiasListBlock,
    CarrosselSolucoesBlock,
    AvisosListBlock,

)

CONTENT_BLOCKS = [
    ('titulo', TituloBlock()),
    ('lista_avisos', AvisosListBlock()),
    ('banner_com_link', BannerComLinkBlock()),
    ('lista_videos', ListaVideosBlock()),
    ('noticias', NoticiasListBlock()),
    ("carrossel_banners", CarrosselBannersBlock()),
    ("carrossel_solucoes", CarrosselSolucoesBlock()),
    ('compromisso', CompromissoBlock()),
]

WIDGET_BLOCKS = [
    ("acessos_rapidos", AcessosRapidosBlock()),
    ("central_monitoramento", OdometerListBlock()),
    ("servicos_online", ServicosOnlineBlock()),
    ('agenda_do_dia', AgendaDoDiaBlock()),
    ('listar_agenda', ListAgendaBlock()),
]

class GrupoIntranet(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Grupo")

    panels = [FieldPanel("nome")]

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Grupo da Intranet"
        verbose_name_plural = "Grupos da Intranet"

class IntranetBase(PageSitePadrao):
    """Página base para todas as páginas internas da Intranet."""
    
    LAYOUT_CHOICES = [
        ('100', 'Layout 1: 100%'),
        ('50_50', 'Layout 2: 50% / 50%'),
        ('60_40', 'Layout 3: 60% / 40%'),
        ('70_30', 'Layout 4: 70% / 30%'),
        ('80_20', 'Layout 5: 80% / 20%'),
        ('35_35_30', 'Layout 6: 35% / 35% / 30%'),
        ('40_40_20', 'Layout 7: 40% / 40% / 20%'),
    ]

    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default='100',
        verbose_name="Layout da Página",
        help_text="Escolha a proporção das colunas de conteúdo."
    )

    coluna_1 = StreamField(
        CONTENT_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Coluna 1"
    )

    coluna_2 = StreamField(
        CONTENT_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Coluna 2"
    )

    widgets = StreamField(
        WIDGET_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Widgets (Coluna Lateral)"
    )

    # Painéis para a aba de Conteúdo
    content_panels = PageSitePadrao.content_panels + [
        FieldPanel('coluna_1'),
        FieldPanel('coluna_2'),
        FieldPanel('widgets'),
    ]

    layout_panels = [
        FieldPanel('layout'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(layout_panels, heading='Layout'),
        ObjectList(PageSitePadrao.promote_panels, heading='Promover'),
        ObjectList(PageSitePadrao.settings_panels, heading='Configurações', classname="settings"),
    ])
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['layout'] = self.layout
        return context

    def serve(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            login_url = f"{settings.LOGIN_URL}?next={self.get_url(request)}"
            return HttpResponseRedirect(login_url)
        return super().serve(request, *args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = "Página Base da Intranet"


class IntranetIndexPage(IntranetBase, PageSitePadraoIndex):
    parent_page_types = None
    subpage_types = ['intranet.IntranetPage']
    max_count = 1

    class Meta:
        verbose_name = "Página Principal da Intranet"


class IntranetPage(IntranetBase):
    parent_page_types = ['intranet.IntranetIndexPage']
    subpage_types = ['intranet.IntranetPage']

    class Meta:
        verbose_name = "Página de Conteúdo da Intranet"
