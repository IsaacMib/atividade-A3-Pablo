"""
Models para o app Para Famílias - Informações para pais e cuidadores.
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


class ResponsaveisPage(PageNeuroAthena):
    """
    Página 'Para Famílias' - Informações para pais e cuidadores.
    
    Subpáginas permitidas:
    - ComoFuncionaPage (Como funciona a triagem)
    - RecursosEducativosPage (Recursos educativos)
    - HistoriasSucessoPage (Histórias de sucesso)
    """
    
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'responsaveis.ComoFuncionaPage',
        'responsaveis.RecursosEducativosPage',
        'responsaveis.HistoriasSucessoPage',
    ]
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('timeline', TimelineBlock()),
            ('faq', FAQBlock()),
            ('cta_section', CTASectionBlock()),
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
        verbose_name = "Página Para Famílias"
        verbose_name_plural = "Páginas Para Famílias"


class ComoFuncionaPage(PageNeuroAthena):
    """
    Página explicando como funciona a triagem.
    """
    
    parent_page_types = ['responsaveis.responsaveisPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('timeline', TimelineBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('image_text', ImageTextBlock()),
            ('faq', FAQBlock()),
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
        verbose_name = "Página Como Funciona"
        verbose_name_plural = "Páginas Como Funciona"


class RecursosEducativosPage(PageNeuroAthena):
    """
    Página de recursos educativos sobre TEA.
    """
    
    parent_page_types = ['responsaveis.responsaveisPage']
    subpage_types = ['responsaveis.RecursoEducativoPage']
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('richtext_section', RichTextSectionBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Recursos Educativos"
        verbose_name_plural = "Páginas Recursos Educativos"


class RecursoEducativoPage(PageNeuroAthena):
    """
    Página individual de um recurso educativo (artigo, guia, vídeo).
    """
    
    parent_page_types = ['responsaveis.RecursosEducativosPage']
    subpage_types = []
    
    tipo_recurso = models.CharField(
        max_length=50,
        choices=[
            ('artigo', 'Artigo'),
            ('guia', 'Guia Prático'),
            ('video', 'Vídeo'),
            ('infografico', 'Infográfico'),
        ],
        default='artigo',
        verbose_name="Tipo de Recurso"
    )
    
    conteudo = StreamField(
        [
            ('richtext_section', RichTextSectionBlock()),
            ('image_text', ImageTextBlock()),
            ('cta_section', CTASectionBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo do recurso"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('tipo_recurso'),
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Recurso Educativo"
        verbose_name_plural = "Recursos Educativos"


class HistoriasSucessoPage(PageNeuroAthena):
    """
    Página com histórias de sucesso de famílias.
    """
    
    parent_page_types = ['responsaveis.responsaveisPage']
    subpage_types = ['responsaveis.HistoriaSucessoPage']
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
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
        verbose_name = "Página Histórias de Sucesso"
        verbose_name_plural = "Páginas Histórias de Sucesso"


class HistoriaSucessoPage(PageNeuroAthena):
    """
    Página individual de uma história de sucesso.
    """
    
    parent_page_types = ['responsaveis.HistoriasSucessoPage']
    subpage_types = []
    
    nome_familia = models.CharField(
        max_length=100,
        verbose_name="Nome da Família (opcional/anônimo)",
        blank=True
    )
    
    conteudo = StreamField(
        [
            ('richtext_section', RichTextSectionBlock()),
            ('testimonial', TestimonialBlock()),
            ('image_text', ImageTextBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da história"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('nome_familia'),
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "História de Sucesso"
        verbose_name_plural = "Histórias de Sucesso"
