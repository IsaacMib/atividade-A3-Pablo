from wagtail.search import index
from django.db import models
from core.models import PageSitePadrao
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

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
  GridImagensBlock,
  ServicoOnlineItemBlock,
  AcordeonBlock,
  FormularioBlock,
)


from blocks.agenda import ListAgendaBlock

class HomePage(PageSitePadrao):
    body = StreamField(
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
            ("list_agenda", ListAgendaBlock()),
            ("carrossel_solucoes", CarrosselSolucoesBlock()),
            ("programa", GridImagensBlock()),
            ("secao_informativa", AcordeonBlock()),
            ("formulario", FormularioBlock()),
          
        ],
        use_json_field=True,
        null=True,
        default=None,
        blank=True,
    )

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('title', partial_match=True),
        index.SearchField('body'),
        index.FilterField('title'),
    ]
    
    content_panels = PageSitePadrao.content_panels + [
        FieldPanel("body"),
    ]
