from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

# from blocks.models import HeadingBlock
from blocks.models import AcessosRapidosBlock, BannerComLinkBlock, ListaVideosBlock, ListRedeSocial, OdometerListBlock, CarrosselBannersBlock,ServicosOnlineBlock

class HomePage(Page):
    body = StreamField(
        [
             ("acessos_rapidos", AcessosRapidosBlock()),
             ('banner_com_link', BannerComLinkBlock()),
             ('lista_videos', ListaVideosBlock()),
             ('redes_sociais',ListRedeSocial()),
             ("central_monitoramento", OdometerListBlock()),
             ("carrossel_banners", CarrosselBannersBlock()),
            ("servicos_online", ServicosOnlineBlock()),
        ],
        use_json_field=True,
        null=True,
        default=None,
        blank=True,
    )

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        context['loop_times'] = range(0, 60)
        return context
    
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
