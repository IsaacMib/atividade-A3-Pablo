from django.db import models
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
from blocks.corpo_tecnico import ListGrupoCorpoTecnicoBlock
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import (
    PageChooserBlock,
)

# Create your models here.

class CorpoTecnicoIndexPage(PageSitePadraoIndex):

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]

    tecnico_em_destaque = PageChooserBlock(
        target_model="paginas.CorpoTecnicoPage",
        required=True,
        label="Técnico em Destaque",
        help_text="Selecione um membro do corpo técnico para destacar na página inicial do corpo técnico."
    )

    grupos_corpo_tecnico = StreamField(
        [
            ('grupo', ListGrupoCorpoTecnicoBlock(required=True, label="Grupo do Corpo Técnico")),
        ],
        verbose_name="Grupos do Corpo Técnico",
        blank=False,
        null=False,
        use_json_field=True
    )

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel('tecnico_em_destaque'),
        FieldPanel('grupos_corpo_tecnico'),
    ]

class CorpoTecnicoGrupoPageIndex(PageSitePadraoIndex):
    
    parent_page_types = [ 'paginas.CorpoTecnicoIndexPage' ]

    titulo = models.CharField(
        verbose_name="Título do Grupo",
        max_length=255,
        blank=False,
        null=False,
        help_text="Título do grupo do corpo técnico."
    )

class CorpoTecnicoPage(PageSitePadrao):

    parent_page_types = [ 'paginas.CorpoTecnicoGrupoPageIndex' ]

    titulo = models.CharField(
        verbose_name="Nome Completo",
        max_length=255,
        blank=False,
        null=False,
        help_text="Nome completo do membro do corpo técnico."
    )

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
    imagem = ImageChooserBlock(
        required=False,
        label="Imagem do membro do corpo técnico."
    )

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel('funcao'),
        FieldPanel('imagem'),
        FieldPanel('bio'),
    ]
