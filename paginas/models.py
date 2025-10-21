from django.db import models
from datetime import datetime
from wagtail.admin.panels import FieldPanel
from core.models import PageSitePadrao, PageSitePadraoIndex


# Create your models here.


class LinhaDoTempoIndex(PageSitePadraoIndex):

    parent_page_types = [
        "home.HomePage",
    ]

    class Meta:
        verbose_name = "Página de Index da Linha do Tempo"


class CardLinhaDoTempoPage(PageSitePadrao):

    imagem = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name='Imagem'
    )
    texto_alternativo = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Texto alternativo da imagem'
    )
    titulo = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Título'
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do aviso", default=datetime.now, blank=True, null=True
    )
    descricao_completa = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Descrição'
    )

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel("imagem"),
        FieldPanel("texto_alternativo"),
        FieldPanel("titulo"),
        FieldPanel("data_publicacao"),
        FieldPanel("descricao_completa"),
    ]

    parent_page_types = [
        "home.HomePage",
    ]

    class Meta:
        verbose_name = "Página de Card da Linha do Tempo"
        # template = 'blocks/card_linha_do_tempo_page.html'
