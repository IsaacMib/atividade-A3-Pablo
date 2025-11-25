from wagtail.search import index
from django.db import models
from core.models import PageNeuroAthena
from django.shortcuts import redirect
from django.contrib import messages
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.contrib.forms.models import AbstractEmailForm
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from modelcluster.fields import ParentalKey

from blocks.models import (
  # AcessosRapidosBlock,  # Específico de governo - não usado no NEUROATHENA
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

# Importar novos blocks criados
from blocks.blocks import (
    TimelineBlock,
    FAQBlock,
    CTASectionBlock,
    TestimonialBlock,
    StatisticsBlock,
    ImageTextBlock,
    RichTextSectionBlock,
)

# from blocks.agenda import ListAgendaBlock  # App agenda foi deletado

class HomePage(PageNeuroAthena):
    """Página inicial do NEUROATHENA."""
    
    body = StreamField(
        [
            # Blocks da HomePage
            ('hero', HeroBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('cta', CTABlock()),
            
            # Blocks genéricos reutilizáveis
            ('timeline', TimelineBlock()),
            ('faq', FAQBlock()),
            ('cta_section', CTASectionBlock()),
            ('testimonial', TestimonialBlock()),
            ('statistics', StatisticsBlock()),
            ('image_text', ImageTextBlock()),
            ('richtext_section', RichTextSectionBlock()),
            
            # Blocks genéricos reutilizáveis
            ('titulo', TituloBlock()),
            ('banner_com_link', BannerComLinkBlock()),
            ('lista_videos', ListaVideosBlock()),
            ('noticias', NoticiasListBlock()),
            ("carrossel_banners", CarrosselBannersBlock()),
            ("programa", GridImagensBlock()),
            ("secao_informativa", AcordeonBlock()),
            ("formulario_customizado", CustomFormBlock()),
            ("linha_do_tempo", LinhaDoTempoBlock()),
        ],
        use_json_field=True,
        null=True,
        default=None,
        blank=True,
    )

    search_fields = PageNeuroAthena.search_fields + [
        index.SearchField('title', partial_match=True),
        index.SearchField('body'),
        index.FilterField('title'),
    ]
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel("body"),
    ]

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            if self._process_custom_form(request):
                return redirect(request.path)
        return super().serve(request, *args, **kwargs)
