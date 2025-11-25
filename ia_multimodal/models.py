"""
Models para o app IA Multimodal - Explicação técnica da Athena.
"""

from django.db import models
from core.models import PageNeuroAthena
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from blocks.blocks import (
    TimelineBlock,
    FAQBlock,
    CTASectionBlock,
    TestimonialBlock,
    StatisticsBlock,
    ImageTextBlock,
    RichTextSectionBlock,
)
from blocks.home import HeroBlock, FeaturesGridBlock


class IAMultimodalPage(PageNeuroAthena):
    """
    Página 'IA Multimodal Athena' - Explicação técnica da IA.
    
    Subpáginas permitidas:
    - ModuloVideoPage (Análise de vídeo/facial)
    - ModuloAudioPage (Análise de áudio/prosódia)
    - ModuloTextoPage (Análise de texto/linguagem)
    - FusaoMultimodalPage (Fusão das modalidades)
    """
    
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'ia_multimodal.ModuloVideoPage',
        'ia_multimodal.ModuloAudioPage',
        'ia_multimodal.ModuloTextoPage',
        'ia_multimodal.FusaoMultimodalPage',
        'ia_multimodal.EticaPrivacidadePage',
    ]
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('image_text', ImageTextBlock()),
            ('statistics', StatisticsBlock()),
            ('faq', FAQBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página IA Multimodal"
        verbose_name_plural = "Páginas IA Multimodal"


class ModuloVideoPage(PageNeuroAthena):
    """
    Página do Módulo de Análise de Vídeo (Facial).
    """
    
    parent_page_types = ['ia_multimodal.IAMultimodalPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('image_text', ImageTextBlock()),
            ('statistics', StatisticsBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Módulo Vídeo"
        verbose_name_plural = "Páginas Módulo Vídeo"


class ModuloAudioPage(PageNeuroAthena):
    """
    Página do Módulo de Análise de Áudio (Prosódia).
    """
    
    parent_page_types = ['ia_multimodal.IAMultimodalPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('image_text', ImageTextBlock()),
            ('statistics', StatisticsBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Módulo Áudio"
        verbose_name_plural = "Páginas Módulo Áudio"


class ModuloTextoPage(PageNeuroAthena):
    """
    Página do Módulo de Análise de Texto (Linguagem).
    """
    
    parent_page_types = ['ia_multimodal.IAMultimodalPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('image_text', ImageTextBlock()),
            ('statistics', StatisticsBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Módulo Texto"
        verbose_name_plural = "Páginas Módulo Texto"


class FusaoMultimodalPage(PageNeuroAthena):
    """
    Página da Fusão Multimodal (CLIP, ImageBind).
    """
    
    parent_page_types = ['ia_multimodal.IAMultimodalPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('image_text', ImageTextBlock()),
            ('statistics', StatisticsBlock()),
            ('timeline', TimelineBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Fusão Multimodal"
        verbose_name_plural = "Páginas Fusão Multimodal"


class EticaPrivacidadePage(PageNeuroAthena):
    """
    Página sobre Ética e Privacidade da IA.
    """
    
    parent_page_types = ['ia_multimodal.IAMultimodalPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('faq', FAQBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Ética e Privacidade"
        verbose_name_plural = "Páginas Ética e Privacidade"
