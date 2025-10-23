from django.db import models
from datetime import datetime
from wagtail.admin.panels import FieldPanel
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import RichTextBlock

# Create your models here.


class LinhaDoTempoIndex(PageSitePadraoIndex):

    parent_page_types = [
        "home.HomePage",
    ]

    class Meta:
        verbose_name = "Página de Index da Linha do Tempo"

    def get_context(self, request):
        context = super().get_context(request)
        context["linha_do_tempo_page"] = LinhaDoTempoPage.objects.live().child_of(self)
        return context

    def get_children(self):
        return super().get_children()


class LinhaDoTempoPage(PageSitePadrao):

    parent_page_types = [
        "linhasdotempo.LinhaDoTempoIndex",
    ]

    class Meta:
        verbose_name = "Página da Linha do Tempo"


class CardLinhaDoTempoPage(PageSitePadrao):

    titulo = models.CharField(
        "Título",
        max_length=255,
        blank=True,
        null=True,
        help_text="Título da página do card da linha do tempo"
    )
    data_evento = models.DateField(
        "Data do evento", default=datetime.now, blank=True, null=True
    )
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
    descricao_completa = StreamField(
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
        verbose_name="Descrição",
        blank=True,
        null=True,
        use_json_field=True,
    )
    data_publicacao = models.DateTimeField(
        "Data de publicação do aviso", default=datetime.now, blank=True, null=True
    )

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel("titulo"),
        FieldPanel("data_evento"),
        FieldPanel("imagem"),
        FieldPanel("texto_alternativo"),
        FieldPanel("descricao_completa"),
        FieldPanel("data_publicacao"),
    ]

    parent_page_types = [
        "linhasdotempo.LinhaDoTempoPage",
    ]

    class Meta:
        verbose_name = "Página de Card da Linha do Tempo"
        # template = 'blocks/card_linha_do_tempo_page.html'
