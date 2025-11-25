"""
Models para o app Para Profissionais - Suíte clínica e recursos.
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


class ProfissionaisPage(PageNeuroAthena):
    """
    Página 'Para Profissionais' - Suíte clínica e recursos.
    
    Subpáginas permitidas:
    - SuiteClinicaPage (Ferramentas da suíte)
    - APIDocumentacaoPage (Documentação API)
    - EstudosValidacaoPage (Estudos científicos)
    """
    
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'profissionais.SuiteClinicaPage',
        'profissionais.APIDocumentacaoPage',
        'profissionais.EstudosValidacaoPage',
    ]
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('statistics', StatisticsBlock()),
            ('image_text', ImageTextBlock()),
            ('cta_section', CTASectionBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Para Profissionais"
        verbose_name_plural = "Páginas Para Profissionais"


class SuiteClinicaPage(PageNeuroAthena):
    """
    Página da Suíte Clínica (Dashboard, ferramentas).
    """
    
    parent_page_types = ['profissionais.ProfissionaisPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('image_text', ImageTextBlock()),
            ('cta_section', CTASectionBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Suíte Clínica"
        verbose_name_plural = "Páginas Suíte Clínica"


class APIDocumentacaoPage(PageNeuroAthena):
    """
    Página de documentação da API para integração.
    """
    
    parent_page_types = ['profissionais.ProfissionaisPage']
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
        verbose_name = "Página Documentação API"
        verbose_name_plural = "Páginas Documentação API"


class EstudosValidacaoPage(PageNeuroAthena):
    """
    Página com estudos e validação científica.
    """
    
    parent_page_types = ['profissionais.ProfissionaisPage']
    subpage_types = ['profissionais.EstudoCientificoPage']
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('statistics', StatisticsBlock()),
            ('testimonial', TestimonialBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Estudos e Validação"
        verbose_name_plural = "Páginas Estudos e Validação"


class EstudoCientificoPage(PageNeuroAthena):
    """
    Página individual de um estudo científico.
    """
    
    parent_page_types = ['profissionais.EstudosValidacaoPage']
    subpage_types = []
    
    autores = models.CharField(
        max_length=500,
        verbose_name="Autores",
        blank=True
    )
    
    publicacao = models.CharField(
        max_length=200,
        verbose_name="Publicação/Journal",
        blank=True
    )
    
    ano = models.IntegerField(
        verbose_name="Ano",
        null=True,
        blank=True
    )
    
    doi = models.CharField(
        max_length=200,
        verbose_name="DOI",
        blank=True
    )
    
    conteudo = StreamField(
        [
            ('richtext_section', RichTextSectionBlock()),
            ('statistics', StatisticsBlock()),
            ('image_text', ImageTextBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo do estudo"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('autores'),
        FieldPanel('publicacao'),
        FieldPanel('ano'),
        FieldPanel('doi'),
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Estudo Científico"
        verbose_name_plural = "Estudos Científicos"
