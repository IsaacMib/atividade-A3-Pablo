from wagtail.search import index
from django.db import models
from core.models import PageSitePadrao
from django.shortcuts import redirect
from django.contrib import messages
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from blocks.models import (
  # AcessosRapidosBlock,  # Específico de governo - não usado no NeuroPrev
  BannerComLinkBlock,
  ListaVideosBlock,
  # OdometerListBlock,  # Central Monitoramento Metabase - não usado
  CarrosselBannersBlock,
  # ServicosOnlineBlock,  # Serviços governamentais - não usado
  TituloBlock,
  NoticiasListBlock,
  # CarrosselSolucoesBlock,  # Soluções governamentais - não usado
  # AvisosListBlock,  # App avisos foi deletado
  GridImagensBlock,
  # ServicoOnlineItemBlock,  # Item serviço governo - não usado
  AcordeonBlock,
  CustomFormBlock,
  LinhaDoTempoBlock
)

from blocks.home import (
    HeroBlock,
    FeaturesGridBlock,
    CTABlock,
)

# from blocks.agenda import ListAgendaBlock  # App agenda foi deletado

class HomePage(PageSitePadrao):
    body = StreamField(
        [
            # Blocks específicos da HomePage
            ('hero', HeroBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('cta', CTABlock()),
            
            # Blocks genéricos reutilizáveis
            ('titulo', TituloBlock()),
            # ('lista_avisos', AvisosListBlock()),  # App avisos foi deletado
            # ("acessos_rapidos", AcessosRapidosBlock()),  # Governo - não usado
            ('banner_com_link', BannerComLinkBlock()),
            ('lista_videos', ListaVideosBlock()),
            # ("central_monitoramento", OdometerListBlock()),  # Metabase - não usado
            ('noticias', NoticiasListBlock()),
            ("carrossel_banners", CarrosselBannersBlock()),
            # ("servicos_online", ServicosOnlineBlock()),  # Governo - não usado
            # ("list_agenda", ListAgendaBlock()),  # App agenda foi deletado
            # ("carrossel_solucoes", CarrosselSolucoesBlock()),  # Governo - não usado
            ("programa", GridImagensBlock()),
            ("secao_informativa", AcordeonBlock()),
            ("formulario_customizado", CustomFormBlock()),
            # ("servico_online_item", ServicoOnlineItemBlock()),  # Governo - não usado
            ("linha_do_tempo", LinhaDoTempoBlock()),
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

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            if self._process_custom_form(request):
                return redirect(request.path)
        return super().serve(request, *args, **kwargs)
