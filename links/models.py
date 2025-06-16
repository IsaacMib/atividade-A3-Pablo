# links/models.py
from django.db import models
from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel



TARGET_CHOICES = [
    ('_self', 'Mesma Aba'),
    ('_blank', 'Nova Aba'),
]



class LinkCabecalhoItemBlock(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título do Link")
    url = models.URLField(max_length=255, verbose_name="URL", help_text="O link no padrão ex.: https://www.detran.pb.gov.br/")
    target = models.CharField(
        max_length=10,
        choices=TARGET_CHOICES,
        default='_self',
        verbose_name="Abrir Link em"
    )

    def __str__(self):
        return self.titulo

    panels = [
        FieldPanel("titulo"),
        FieldPanel("url"),
        FieldPanel("target"),
    ]

    class Meta:
        verbose_name = "Link do Menu"
        verbose_name_plural = "Links do Menu"
        ordering = ['titulo']

"""
register = template.Library()

TARGET_CHOICES = [
    ('_self', 'Mesma Aba'),
    ('_blank', 'Nova Aba'),
]

class LinkCabecalhoItemBlock(StructBlock):
    titulo = CharBlock(max_length=255, verbose_name="Título do Link")
    url = URLBlock(max_length=255, verbose_name="URL", help_text="O link no padrão ex.: https://www.detran.pb.gov.br/")
    target = ChoiceBlock(
        choices=TARGET_CHOICES,
        default='_self',
        verbose_name="Abrir Link em"
    )

    class Meta:
        icon = 'link'
        template = 'sitepadrao/templates/header.html'
        label = 'Link do Cabeçalho'


"""
