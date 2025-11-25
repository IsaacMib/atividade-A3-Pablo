"""
Models para o app Institucional - Sobre Nós, Missão, Equipe e Parcerias do NEUROATHENA.
"""

from django.db import models
from core.models import PageNeuroAthena, PageNeuroAthenaIndex
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from blocks.institucional import LocalizacaoBlock

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

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

class InstitucionalIndexPage(PageNeuroAthenaIndex):
    """
    Página principal Institucional - Sobre Nós, Missão, Equipe e Parcerias.
    """
    
    subpage_types = [
        'institucional.SobreNosPage',
        'institucional.MissaoVisaoPage', 
        'institucional.EquipePage',
        'institucional.ParceriasPage',
        'institucional.LocalizacaoPage',
    ]

    parent_page_types = ['home.HomePage']

    def get_context(self, request):
        context = super(InstitucionalIndexPage, self).get_context(request)
        all_posts = self.get_children().live().public().order_by('-first_published_at')
        paginator = Paginator(all_posts, 10)  # 10 posts por página
        page_number = request.GET.get('page')
        try:
            all_posts = paginator.page(page_number)
        except PageNotAnInteger:
            all_posts = paginator.page(1)
        except EmptyPage:
            all_posts = paginator.page(paginator.num_pages)
        # Adiciona os posts ao contexto
        context['posts'] = all_posts
        return context

    class Meta:
        verbose_name = "Página Index Institucional"
        verbose_name_plural = "Páginas Institucionais"


class LocalizacaoPage(PageNeuroAthena):

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    
    body = StreamField([
        ("localizacoes", LocalizacaoBlock()),
    ],
    blank=True,
    use_json_field=True,
    verbose_name="Conteúdo da página"
    )

    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = "Página de Localização"
        verbose_name_plural = "Páginas de Localização"


class SobreNosPage(PageNeuroAthena):
    """
    Página 'Sobre Nós' - História e Missão do NEUROATHENA.
    """
    
    parent_page_types = ['institucional.InstitucionalIndexPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('image_text', ImageTextBlock()),
            ('statistics', StatisticsBlock()),
            ('timeline', TimelineBlock()),
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
        verbose_name = "Página Sobre Nós"
        verbose_name_plural = "Páginas Sobre Nós"


class MissaoVisaoPage(PageNeuroAthena):
    """
    Página de Missão, Visão e Valores.
    """
    
    parent_page_types = ['institucional.InstitucionalIndexPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
            ('image_text', ImageTextBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Missão e Visão"
        verbose_name_plural = "Páginas Missão e Visão"


class EquipePage(PageNeuroAthena):
    """
    Página da Equipe Técnica.
    """
    
    parent_page_types = ['institucional.InstitucionalIndexPage']
    subpage_types = ['institucional.MembroEquipePage']
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da página"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Página Equipe"
        verbose_name_plural = "Páginas Equipe"


class MembroEquipePage(PageNeuroAthena):
    """
    Página individual de um membro da equipe.
    """
    
    parent_page_types = ['institucional.EquipePage']
    subpage_types = []
    
    cargo = models.CharField(
        max_length=100,
        verbose_name="Cargo",
        blank=True
    )
    
    especialidade = models.CharField(
        max_length=200,
        verbose_name="Especialidade",
        blank=True
    )
    
    conteudo = StreamField(
        [
            ('richtext_section', RichTextSectionBlock()),
            ('image_text', ImageTextBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Biografia e informações"
    )
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('cargo'),
        FieldPanel('especialidade'),
        FieldPanel('conteudo'),
    ]
    
    class Meta:
        verbose_name = "Membro da Equipe"
        verbose_name_plural = "Membros da Equipe"


class ParceriasPage(PageNeuroAthena):
    """
    Página de Parcerias Institucionais.
    """
    
    parent_page_types = ['institucional.InstitucionalIndexPage']
    subpage_types = []
    
    conteudo = StreamField(
        [
            ('hero', HeroBlock()),
            ('richtext_section', RichTextSectionBlock()),
            ('features_grid', FeaturesGridBlock()),
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
        verbose_name = "Página Parcerias"
        verbose_name_plural = "Páginas Parcerias"