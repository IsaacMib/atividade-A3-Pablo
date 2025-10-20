from django.db import models
from django.http import HttpResponseRedirect
from django.conf import settings
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail import (blocks)
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

# -------------------------------------------------------------
# MODELOS AUXILIARES
# -------------------------------------------------------------

class GrupoIntranet(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Grupo")

    panels = [FieldPanel("nome")]

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Grupo da Intranet"
        verbose_name_plural = "Grupos da Intranet"


class IntranetColumnBlock(blocks.StructBlock):
    coluna = blocks.ChoiceBlock(
        choices=[
            ('coluna_1', 'Primeira Coluna'),
            ('coluna_2', 'Segunda Coluna'),
            ('coluna_3', 'Widgets'),
        ],
        default='coluna_1',
        label="Posição do bloco na página"
    )

    conteudo = blocks.StreamBlock(
        [
            ('titulo', TituloBlock()),
            ('lista_avisos', AvisosListBlock()),
            ("acessos_rapidos", AcessosRapidosBlock()),
            ('banner_com_link', BannerComLinkBlock()),
            ('lista_videos', ListaVideosBlock()),
            ("central_monitoramento", OdometerListBlock()),
            ('noticias', NoticiasListBlock()),
            ("carrossel_banners", CarrosselBannersBlock()),
            ("servicos_online", ServicosOnlineBlock()),
            ("carrossel_solucoes", CarrosselSolucoesBlock()),
            ('agenda_do_dia', AgendaDoDiaBlock()),
            ('listar_agenda', ListAgendaBlock()),
            ('compromisso', CompromissoBlock()),
        ],
        required=True,
        label="Conteúdo do bloco"
    )


# -------------------------------------------------------------
# PÁGINAS
# -------------------------------------------------------------

class IntranetBase(PageSitePadrao):
    """Página base para todas as páginas internas da Intranet."""

    body = StreamField(
        [
            ('coluna', IntranetColumnBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da Página"
    )

    content_panels = PageSitePadrao.content_panels + [FieldPanel('body')]

    def get_layout_context(self):
        
        """Determina o layout da página com base nos blocos presentes."""
        
        col1_blocks = []
        col2_blocks = []
        widget_blocks = []
        
        # percorre o StreamField principal
        for block in self.body:

            if block.block_type == 'coluna' and block.value['conteudo']:
                coluna = block.value['coluna']
                if coluna == 'coluna_1':
                    col1_blocks.append(block)
                elif coluna == 'coluna_2':
                    col2_blocks.append(block)
                elif coluna == 'coluna_3':
                    widget_blocks.append(block)
            
        has_col1 = bool(col1_blocks)
        has_col2 = bool(col2_blocks)
        has_widget = bool(widget_blocks)
        
        if has_col1 and has_col2 and has_widget:
            layout = "40_40_20"
        elif has_col1 and has_col2:
            layout = "50_50"
        elif (has_col1 or has_col2) and has_widget:
            layout = "70_30"
        elif has_col1:
            layout = "100_col1"
        elif has_col2:
            layout = "100_col2"
        elif has_widget:
            layout = "100_widget"
        else:
            layout = "100_default"

            
        return {
            "col1_blocks": col1_blocks,
            "col2_blocks": col2_blocks,
            "widget_blocks": widget_blocks,
            "layout": layout,
       }
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        layout_context = self.get_layout_context()
        context.update(layout_context)
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
    """Página inicial da Intranet, com suporte a colunas e modo reduzido."""
    parent_page_types = None
    subpage_types = ['intranet.IntranetPage']
    max_count = 1

    class Meta:
        verbose_name = "Página Principal da Intranet"


class IntranetPage(IntranetBase):
    """Páginas internas da Intranet."""
    parent_page_types = ['intranet.IntranetIndexPage']
    subpage_types = ['intranet.IntranetPage']

    class Meta:
        verbose_name = "Página de Conteúdo da Intranet"
