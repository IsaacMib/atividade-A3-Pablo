from django.db import models
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
from blocks.corpo_tecnico import ListGrupoCorpoTecnicoBlock

# Create your models here.

class CorpoTecnicoIndexPage(PageSitePadraoIndex):

    grupos_corpo_tecnico = StreamField(
        [
            ('grupo', ListGrupoCorpoTecnicoBlock(required=True, label="Grupo do Corpo Técnico")),
        ],
        verbose_name="Grupos do Corpo Técnico",
        blank=True,
        null=True,
        use_json_field=True
    )

class CorpoTecnicoGrupoPageIndex(PageSitePadraoIndex):
    titulo = models.CharField(
        verbose_name="Título do Grupo",
        max_length=255,
        blank=False,
        null=False,
        help_text="Título do grupo do corpo técnico."
    )

class CorpoTecnicoPage(PageSitePadrao):

    nome = models.CharField(
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
    imagem = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem",
        help_text="Imagem do membro do corpo técnico."
    )
