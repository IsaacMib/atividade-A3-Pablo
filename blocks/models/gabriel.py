import requests
import json
from django.core.cache import cache
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    ListBlock, 
    FloatBlock,
    PageChooserBlock, 
    URLBlock,
    IntegerBlock,
)
from wagtail.embeds.blocks import EmbedBlock
from django.utils.functional import cached_property


from django.core.exceptions import ValidationError

_CACHE_TIMEOUT = 600  # 10 minutos em segundos

class OdometerBlock(StructBlock):
    # Campos não editáveis pelo usuário
    odometer_description = CharBlock(required=True, max_length=100, label="Descrição do Dado")
    odometer_value = FloatBlock(required=False, label="Valor do Dado Default", help_text="Preenchido automaticamente pela API", disabled=True)
    id_card = CharBlock(required=True, label="ID do Card do Metabase")

    def get_context(self, value, parent_context=None):
        from django.conf import settings
        context = super().get_context(value, parent_context=parent_context)
        id_card = value['id_card']
        url = f"{settings.METABASE_API_URL}{id_card}"
        headers = {
          'x-api-key': settings.METABASE_API_KEY
        }
        cache_key = f"metabase_odometer_value_{id_card}"
        data = cache.get(cache_key)
        if data is None:
            try:
                response = requests.get(url, headers=headers)
                if response.ok:
                    response_json = response.json()
                    result_metadata = response_json.get('result_metadata', [])
                    if result_metadata:
                        metabase_value = result_metadata[0].get('fingerprint', {}).get('type', {}).get('type/Number',{}).get('q1', 0)
                    else:
                        metabase_value = value['odometer_value']
                else:
                    metabase_value = value['odometer_value']
                cache.set(cache_key, metabase_value, timeout=_CACHE_TIMEOUT)
            except Exception as e:
                metabase_value = value['odometer_value']
        else:
            metabase_value = data
        context['self'].metabase_value = metabase_value
        context['id_card'] = id_card
        return context

    class Meta:
        template = 'blocks/odometer.html'
        icon = 'plus'
        label = 'Odometer'

class OdometerListBlock(StructBlock):
    odometers = ListBlock(OdometerBlock(), label="Central de Monitoramento Detran")

    class Meta:
        template = 'blocks/central_monitoramento_detran.html'
        icon = 'list-ul'
        label = 'Central de Monitoramento Detran'

class NoticiasListBlock(StructBlock):
    noticias_index_page = PageChooserBlock(
        required=True,
        target_model='noticias.NoticiasIndexPages',
        help_text="Selecione a página de índice de notícias"
    )
    quantidade = IntegerBlock(
        required=False,
        default=6,
        min_value=1,
        label="Quantidade de notícias exibidas"
    )
    texto_link = CharBlock(
        required=False,
        default="Ver todas as notícias",
        label="Texto do link para todas as notícias"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        noticias_index_page = value.get('noticias_index_page')
        quantidade = value.get('quantidade') or 6
        texto_link = value.get('texto_link') or "Ver todas as notícias"
        noticias = []
        noticias_index_page_url = None
        if noticias_index_page:
            noticias = noticias_index_page.get_ultimas_noticias(quantidade=quantidade)
            noticias_index_page_url = noticias_index_page.url
        context['noticias'] = noticias
        context['noticias_index_page_url'] = noticias_index_page_url
        context['texto_link'] = texto_link
        return context

    class Meta:
        template = 'blocks/list_noticias.html'
        icon = 'list-ul'
        label = 'Lista de Notícias'


class LinkStructBlock(StructBlock):
    link_text = CharBlock(required=True, help_text="Texto")
    internal_page = PageChooserBlock(required=False, help_text="Link para uma página interna")
    external_url = URLBlock(required=False, help_text="Ou insira uma URL externa")

    def clean(self, value):
        cleaned_data = super().clean(value)
        if not cleaned_data.get('internal_page') and not cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer um link interno ou externo.')
        if cleaned_data.get('internal_page') and cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer apenas 1 link.')
        return cleaned_data

    def get_url(self, value):
        if value.get('internal_page'):
            return value['internal_page'].url
        return value.get('external_url')

    class Meta:
        icon = 'link'
        label = 'Link'

class LinkWithImageStructBlock(StructBlock):
    link_text = RichTextBlock(required=True, help_text="Texto")
    internal_page = PageChooserBlock(required=False, help_text="Link para uma página interna")
    external_url = URLBlock(required=False, help_text="Ou insira uma URL externa")
    image = ImageChooserBlock(required=False, help_text="Imagem opcional para o link")

    def clean(self, value):
        cleaned_data = super().clean(value)
        if not cleaned_data.get('internal_page') and not cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer um link interno ou externo.')
        if cleaned_data.get('internal_page') and cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer apenas 1 link.')
        return cleaned_data

    def get_url(self, value):
        if value.get('internal_page'):
            return value['internal_page'].url
        return value.get('external_url')

    class Meta:
        icon = 'link'
        label = 'Link'


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headers
    """

    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(
        choices=[
            ("", "Select a header size"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"
        preview_value = {"heading_text": "Healthy bread types", "size": "h2"}
        description = "Titulo com tamanho selecionável (H2, H3, H4)"

class CaptionedImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    @cached_property
    def preview_image(self):
        # Cache the image object for previews to avoid repeated queries
        return get_image_model().objects.last()

    def get_preview_value(self):
        return {
            **self.meta.preview_value,
            "image": self.preview_image,
            "caption": self.preview_image.description,
        }

    class Meta:
        icon = "image"
        template = "blocks/captioned_image_block.html"
        preview_value = {"attribution": "The Wagtail Bakery"}
        description = "An image with optional caption and attribution"

class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author
    """

    text = TextBlock()
    attribute_name = CharBlock(blank=True, required=False, label="e.g. Mary Berry")

    class Meta:
        icon = "openquote"
        template = "blocks/blockquote.html"
        preview_value = {
            "text": (
                "If you read a lot you're well read / "
                "If you eat a lot you're well bread."
            ),
            "attribute_name": "Willie Wagtail",
        }
        description = "A quote with an optional attribution"

# StreamBlocks
class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """

    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(
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
    )
    image_block = CaptionedImageBlock()
    block_quote = BlockQuote()
    embed_block = EmbedBlock(
        help_text="Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
        icon="media",
        template="blocks/embed_block.html",
        preview_template="blocks/preview/static_embed_block.html",
        preview_value="https://www.youtube.com/watch?v=mwrGSfiB1Mg",
        description="An embedded video or other media",
    )