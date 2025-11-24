"""
Wagtail home page models.
"""
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class HomePage(Page):
    """
    Home Page model.
    """
    body = RichTextField(
        blank=True,
        verbose_name='Conteúdo'
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
    
    class Meta:
        verbose_name = 'Página Inicial'
        verbose_name_plural = 'Páginas Iniciais'
