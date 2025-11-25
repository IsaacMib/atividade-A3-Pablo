from django.db import models
from datetime import datetime
from wagtail.admin.panels import FieldPanel
from core.models import PageNeuroAthena, PageNeuroAthenaIndex
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import (
    RichTextBlock,
)

from blocks.models import (
    ListaVideosBlock,
)

# Create your models here.


class LinhaDoTempoIndex(PageNeuroAthenaIndex):

    parent_page_types = [
        "home.HomePage",
    ]

    subpage_types = [
        "linhasdotempo.LinhaDoTempoPage",
    ]

    class Meta:
        verbose_name = "Página de Listagem de Diferentes Linhas do Tempo"

    def get_context(self, request):
        context = super().get_context(request)
        context["linha_do_tempo_page"] = LinhaDoTempoPage.objects.live().child_of(self)
        return context

    def get_children(self):
        return super().get_children()


class LinhaDoTempoPage(PageNeuroAthena):

    parent_page_types = [
        "linhasdotempo.LinhaDoTempoIndex",
    ]

    subpage_types = [
        "linhasdotempo.CardLinhaDoTempoPage",
    ]

    class Meta:
        verbose_name = "Página da Linha do Tempo"

    def get_context(self, request):
        context = super().get_context(request)
        context["cards"] = CardLinhaDoTempoPage.objects.live().child_of(
            self).order_by("data_evento")
        return context


class CardLinhaDoTempoPage(PageNeuroAthena):

    parent_page_types = [
        "linhasdotempo.LinhaDoTempoPage",
    ]

    subpage_types = []

    data_evento = models.DateField(
        "Data do evento", default=datetime.now, blank=True, null=True
    )
    images = StreamField(
        [
            ("imagem", ImageChooserBlock(required=True, label="Imagem do conteúdo")),
        ],
        verbose_name="Coleção de Imagens",
        blank=False,
        null=False,
        use_json_field=True,
        help_text="Adicione uma ou mais imagens para esta linha do tempo."
    )
    # Removed texto_alternativo field as it's now handled per-image
    descricao_linha_do_tempo = StreamField(
        [
            ("paragraph", RichTextBlock(
                icon="pilcrow",
                template="blocks/paragraph_block.html",
                preview_value=(
                    """
                        <h2>Our bread pledge</h2>
                        <p>As a bakery, <b>breads</b> have <i>always</i> been in our hearts.
                        <a href="https://en.wikipedia.org/wiki/Staple_food">Staple foods</a>
                        are essential for society, and – bread is the tastiest of all.
                        We love to transform batters and doughs into baked goods with a firm
                        dry crust and fluffy center.</p>
                        """
                ),
                description="A rich text paragraph",
            )),
        ],
        verbose_name="Descrição de marco da linha do tempo",
        blank=False,
        null=False,
        use_json_field=True,
    )

    lista_videos = StreamField(
        [
            ('lista_videos', ListaVideosBlock()),
        ],
        verbose_name="Lista de vídeos",
        help_text="Adicione vídeos à página do card de linha do tempo",
        max_num=3,
        blank=True,
        null=True,
        use_json_field=True,
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do aviso", default=datetime.now, blank=True, null=True
    )

    content_panels = [
        PageNeuroAthena.content_panels[0],  # Título da página
        FieldPanel("data_evento"),
        FieldPanel("images"),
        FieldPanel("descricao_linha_do_tempo"),
        FieldPanel("lista_videos"),
        FieldPanel("data_publicacao"),
    ]

    parent_page_types = [
        "linhasdotempo.LinhaDoTempoPage",
    ]

    class Meta:
        verbose_name = "Página de Card da Linha do Tempo"

    @property
    def imagem(self):
        """Retorna a primeira imagem da StreamField 'images' ou None se estiver vazia."""
        if self.images and len(self.images) > 0:
            return self.images[0].value
        return None

    @property
    def detail_page(self):
        return self

    def get_url(self, request=None, *args, **kwargs):
        return super().get_url(request=request, *args, **kwargs)
