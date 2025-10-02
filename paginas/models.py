from django.db import models
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
from blocks.corpo_tecnico import ListGrupoCorpoTecnicoBlock
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import (
    PageChooserBlock,
)

from wagtail.models.panels import PanelPlaceholder

# Create your models here.

class CorpoTecnicoIndexPage(PageSitePadraoIndex):

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    subpage_types = ['paginas.CorpoTecnicoGrupoPageIndex']

    tecnico_em_destaque = models.ForeignKey(
        'paginas.CorpoTecnicoPage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Técnico em Destaque",
        help_text="Selecione um membro do corpo técnico para destacar na página inicial do corpo técnico."
    )

    grupos_corpo_tecnico = StreamField(
        [
            ('grupo', ListGrupoCorpoTecnicoBlock(label="Grupo do Corpo Técnico")),
        ],
        verbose_name="Grupos do Corpo Técnico",
        null=True,
        blank=True,
    )

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel('tecnico_em_destaque'),
        FieldPanel('grupos_corpo_tecnico'),
    ]

class CorpoTecnicoGrupoPageIndex(PageSitePadraoIndex):
    
    parent_page_types = [ 'paginas.CorpoTecnicoIndexPage' ]
    subpage_types = ['paginas.CorpoTecnicoPage']

class CorpoTecnicoPage(PageSitePadrao):

    parent_page_types = [ 'paginas.CorpoTecnicoGrupoPageIndex' ]
    subpage_types = []

    funcao = models.CharField(
        verbose_name="Função",
        max_length=255,
        blank=True,
        null=True,
        help_text="Função ou cargo do membro do corpo técnico."
    )
    bio = models.TextField(
        verbose_name="Biografia",
        blank=True,
        null=True,
        help_text="Breve biografia do membro do corpo técnico."
    )
    
    imagem = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Imagem",
        help_text="Imagem do membro do corpo técnico."
    )

    content_panels = [
        TitleFieldPanel('title', 
            placeholder="Nome do Membro", 
            help_text="Nome completo do membro do corpo técnico."),
        FieldPanel('funcao'),
        FieldPanel('imagem'),
        FieldPanel('bio'),
    ]
