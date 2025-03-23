from django.core.validators import validate_slug
from wagtail import blocks as wagtail_blocks
from wagtail_color_panel.blocks import NativeColorBlock



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