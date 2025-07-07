from wagtail.search import index
from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from blocks.models import AcessosRapidosBlock, BannerComLinkBlock, ListaVideosBlock, OdometerListBlock, CarrosselBannersBlock, ServicosOnlineBlock, TituloBlock, NoticiasListBlock

class HomePage(Page):
    body = StreamField(
        [
            ('titulo', TituloBlock()),
            ("acessos_rapidos", AcessosRapidosBlock()),
            ('banner_com_link', BannerComLinkBlock()),
            ('lista_videos', ListaVideosBlock()),
            ("central_monitoramento", OdometerListBlock()),
            ('noticias', NoticiasListBlock()),
            ("carrossel_banners", CarrosselBannersBlock()),
            ("servicos_online", ServicosOnlineBlock()),
        ],
        use_json_field=True,
        null=True,
        default=None,
        blank=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField('title', partial_match=True),
        index.SearchField('body'),
        index.FilterField('title'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
