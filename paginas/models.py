from django.db import models
from wagtail.admin.panels import FieldPanel
from core.models import PageSitePadrao, PageSitePadraoIndex


# Create your models here.
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
        FieldPanel("descricao_completa"),
    ]

    parent_page_types = [
        "home.HomePage",
    ]
    
    class Meta:
        verbose_name = "Página de Card da Linha do Tempo"
        # template = 'blocks/card_linha_do_tempo_page.html'

