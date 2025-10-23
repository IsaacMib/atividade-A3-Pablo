from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks

class LGPD(Page):
    subtitle = models.CharField(
        verbose_name="Subtítulo",
        blank=True,
        max_length=255
    )

    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        max_length=500,
        help_text="Breve descrição do conteúdo da página."
    )

    banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Banner da página"
    )

    lgpd_text = models.TextField(
        verbose_name="Texto LGPD",
        blank=True,
        help_text="Texto sobre proteção de dados e privacidade"
    )

    corpo = StreamField([
        ('titulo_texto', blocks.StructBlock([
            ('titulo', blocks.CharBlock(required=True, label="Título")),
            ('texto', blocks.RichTextBlock(required=True, label="Texto")),
        ], label="Título e Texto")),
    ], verbose_name="Conteúdo da página", blank=True, null=True, use_json_field=True)

    template = "lgpd/lgpd_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("descricao"),
        FieldPanel("banner"),  
        FieldPanel("lgpd_text"),
        FieldPanel("corpo"),
    ]

    parent_page_types = ["home.HomePage"] 
    subpage_types = [] 

    class Meta:
        verbose_name = "LGPD"
        verbose_name_plural = "LGPD"