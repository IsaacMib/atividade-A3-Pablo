# links/models.py
from django.db import models
from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel,InlinePanel
from wagtail.models import Orderable, ParentalKey
from modelcluster.models import ClusterableModel



TARGET_CHOICES = [
    ('_self', 'Mesma Aba'),
    ('_blank', 'Nova Aba'),
]



class LinkCabecalhoItemBlock(ClusterableModel):
    titulo = models.CharField(max_length=255, verbose_name="Título do Link")
    url = models.URLField(max_length=255, verbose_name="URL", help_text="O link no padrão ex.: https://www.codata.pb.gov.br/")
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
        InlinePanel("submenus", label="Submenus"), 
    ]

    class Meta:
        verbose_name = "Link do Menu"
        verbose_name_plural = "Links do Menu"
        ordering = ['titulo']



class SubMenuItem(Orderable):
    parent = ParentalKey(
        'LinkCabecalhoItemBlock',
        related_name='submenus',
        on_delete=models.CASCADE,
    )
    titulo = models.CharField(max_length=255, verbose_name="Título do Submenu")
    url = models.URLField(max_length=255, verbose_name="URL")
    target = models.CharField(
        max_length=10,
        choices=TARGET_CHOICES,
        default='_self',
        verbose_name="Abrir Link em"
    )

    panels = [
        FieldPanel("titulo"),
        FieldPanel("url"),
        FieldPanel("target"),
    ]

    def __str__(self):
        return f"{self.parent.titulo} > {self.titulo}"

    class Meta:
        ordering = ['sort_order']

"""
register = template.Library()

TARGET_CHOICES = [
    ('_self', 'Mesma Aba'),
    ('_blank', 'Nova Aba'),
]

class LinkCabecalhoItemBlock(StructBlock):
    titulo = CharBlock(max_length=255, verbose_name="Título do Link")
<<<<<<< HEAD
    url = URLBlock(max_length=255, verbose_name="URL", help_text="O link no padrão ex.: https://www.detran.pb.gov.br/")
=======
    url = URLBlock(max_length=255, verbose_name="URL", help_text="O link no padrão ex.: https://www.codata.pb.gov.br/")
>>>>>>> site-padrao-main
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
