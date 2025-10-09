from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField, RichTextField
from wagtail.contrib.routable_page.models import RoutablePageMixin

from core.models import PageSitePadrao, PageSitePadraoIndex
from blocks.models import EspecificDocumentChooserBlock

from datetime import datetime
from collections import defaultdict

from wagtail.blocks import (
    CharBlock,
    RichTextBlock,
    StructBlock,
    ListBlock,
    DateTimeBlock,
    URLBlock,
    StreamBlock,
)


SITUACAO_EDITAL_CHOICES = [
    ('aberto', 'Aberto'),
    ('em_andamento', 'Em Andamento'),
    ('encerrado', 'Encerrado'),
    ('suspenso', 'Suspenso'),
    ('cancelado', 'Cancelado'),
]


class AnexoChoiceBlock(StreamBlock):
    arquivo = StructBlock([
        ('nome_documento', CharBlock(required=True, label="Nome para exibição do arquivo")),
        ('documento', EspecificDocumentChooserBlock(required=True, label="Arquivo")),
    ], label="Arquivo", icon="doc-full-inverse")

    link_externo = StructBlock([
        ('nome_link', CharBlock(required=True, label="Nome para exibição do link")),
        ('url', URLBlock(required=True, label="URL do link externo")),
    ], label="Link Externo", icon="link")

    class Meta:
        label = "Anexo"
        max_num = 1


class FaseEditalBlock(StructBlock):
    titulo_fase = CharBlock(required=True, label="Título da Fase")
    data_fase = DateTimeBlock(required=True, label="Data e Hora da Fase")
    anexo = AnexoChoiceBlock(required=False)

    class Meta:
        icon = 'date'
        label = "Fase do Edital"
        template = 'fase_edital_block.html'


class EditalPage(PageSitePadrao):
    numero = models.CharField(max_length=50, verbose_name="Número do Edital")
    ano = models.IntegerField(verbose_name="Ano do Edital", default=datetime.now().year)
    descricao = RichTextField(
        verbose_name="Descrição do Edital",
        help_text="Breve descrição sobre o objetivo do edital."
    )
    data_publicacao = models.DateField(
        "Data de publicação do edital", default=datetime.today
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_EDITAL_CHOICES,
        default='aberto',
        verbose_name="Situação do Edital"
    )

    fases_edital = StreamField(
        [("fase", FaseEditalBlock())],
        verbose_name="Fases do Edital (Ciclo de Vida)",
        help_text="Adicione as fases do edital, como abertura, inscrições, retificações, resultados, etc.",
        use_json_field=True,
        blank=True
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('numero'),
            FieldPanel('ano'),
            FieldPanel('situacao'),
            FieldPanel('data_publicacao'),
        ], heading="Informações Principais do Edital"),
        FieldPanel('descricao', classname="full"),
        FieldPanel('fases_edital'),
    ]

    parent_page_types = ['editais.EditaisIndexPage']
    subpage_types = []

    template = "edital_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Ordena as fases do edital pela data da fase (da mais antiga para a mais nova)
        if self.fases_edital:
            context['fases_ordenadas'] = sorted(self.fases_edital, key=lambda fase: fase.value['data_fase'])

        return context

    class Meta:
        verbose_name = "Página de Edital"
        verbose_name_plural = "Páginas de Editais"


class EditaisIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    parent_page_types = ['home.HomePage']
    subpage_types = ['editais.EditalPage']

    template = "editais_index_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        editais = EditalPage.objects.live().descendant_of(self).order_by('-ano', '-data_publicacao')

        editais_por_ano = defaultdict(list)
        for edital in editais:
            editais_por_ano[edital.ano].append(edital)

        context['editais_por_ano'] = sorted(editais_por_ano.items(), key=lambda x: x[0], reverse=True)
        return context

    class Meta:
        verbose_name = "Página de Índice de Editais"
