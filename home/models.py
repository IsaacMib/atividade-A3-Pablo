from wagtail.search import index
from django.db import models
from core.models import PageSitePadrao
from django.shortcuts import redirect
from django.contrib import messages
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
  CustomFormBlock,
  LinhaDoTempoBlock
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
            ("formulario_customizado", CustomFormBlock()),
            ("servico_online_item", ServicoOnlineItemBlock()),
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
