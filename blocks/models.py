from django.core.validators import validate_slug
from wagtail import blocks as wagtail_blocks
from wagtail_color_panel.blocks import NativeColorBlock
from wagtail.blocks import PageChooserBlock, URLBlock, CharBlock, RichTextBlock
from wagtail.images.blocks import ImageChooserBlock

from django.core.exceptions import ValidationError


class LinkStructBlock(wagtail_blocks.StructBlock):
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

class LinkWithImageStructBlock(wagtail_blocks.StructBlock):
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


class HeadingBlock(wagtail_blocks.StructBlock):
    heading_level = wagtail_blocks.ChoiceBlock(
        choices=[
            ("h2", "Level 2 (child of level 1)"),
            ("h3", "Level 3 (child of level 2)"),
            ("h4", "Level 4 (child of level 3)"),
            ("h5", "Level 5 (child of level 4)"),
            ("h6", "Level 6 (child of level 5)"),
        ],
        help_text="These different heading levels help to communicate the organization and hierarchy of the content on a page.",  # noqa: E501
    )
    heading_text = wagtail_blocks.CharBlock(
        help_text="The text to appear in the heading.",
    )
    target_slug = wagtail_blocks.CharBlock(
        help_text="Used to link to a specific location within this page. A slug should only contain letters, numbers, underscore (_), or hyphen (-).",  # noqa: E501
        validators=(validate_slug,),
        required=False,
    )
    color = NativeColorBlock(
        required=False,
    )

    class Meta:
        icon = "list-ol"
        template = "blocks/heading.html"
