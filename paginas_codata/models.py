from datetime import datetime
from django.db import models
from wagtail.models import Page
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect, render

from wagtail.fields import StreamField
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import (
    ObjectList, FieldPanel, MultiFieldPanel, TabbedInterface
)
from wagtail.images.blocks import ImageChooserBlock

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from core.models import PageSitePadrao, PageSitePadraoIndex
from blocks.models import BaseStreamBlock, EspecificDocumentChooserBlock
from core.utils import (
    get_file_type,
    get_fontawesome_file_icon,
    get_page_title_with_counter,
    get_widget_input_with_counter
)


# ============================================================
#                   CLASSE BASE ABSTRATA
# ============================================================

class AvisosDefaultPage(PageSitePadrao):
    """
    Classe base abstrata para páginas de Avisos e Eventos.
    Centraliza campos e métodos comuns para evitar duplicação de código.
    """
    descricao = models.TextField(
        "Descrição",
        help_text="Breve descrição do conteúdo da página.",
        max_length=255
    )

    data_publicacao = models.DateTimeField(
        "Data de publicação",
        default=datetime.now,
        blank=True,
        null=True
    )

    body = StreamField(
        BaseStreamBlock(),
        verbose_name="Corpo da página",
        blank=True,
        null=True,
        use_json_field=True
    )

    body_migrated = models.TextField(
        "Conteúdo migrado do Plone",
        help_text="Usado apenas para conteúdo do antigo site Plone.",
        blank=True,
        null=True
    )

    plone_node_id = models.TextField(
        "ID Plone",
        blank=True,
        null=True,
        db_index=True,
        unique=True,
        help_text="ID do nó no Plone, usado para identificar a página migrada."
    )

    sensivel_periodo_eleitoral = models.BooleanField(
        "Sensível ao período eleitoral",
        default=False,
        help_text="Marque se este conteúdo deve ser ocultado durante o período eleitoral."
    )

    arquivos = StreamField(
        [("arquivo", EspecificDocumentChooserBlock(required=True, label="Arquivos"))],
        verbose_name="Arquivos",
        blank=True,
        null=True,
        use_json_field=True,
    )

    nao_exibir_lista_de_arquivos = models.BooleanField(
        "Não exibir lista de arquivos",
        default=False,
        help_text="Marque para ocultar a lista de arquivos.",
    )

    content_panels = get_page_title_with_counter(100) + [
        FieldPanel("descricao", widget=get_widget_input_with_counter()),
        MultiFieldPanel(
            [
                FieldPanel("nao_exibir_lista_de_arquivos"),
                FieldPanel("arquivos"),
            ],
            heading="Arquivos"
        ),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
    ]

    settings_panels = PageSitePadrao.settings_panels + [
        FieldPanel("sensivel_periodo_eleitoral"),
    ]

    migracao_panels = [FieldPanel("body_migrated")]

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('body'),
        index.SearchField('descricao'),
    ]

    @staticmethod
    def get_arquivo_icon(arquivo):
        """Retorna o ícone correspondente ao tipo de arquivo."""
        file_info = get_file_type(arquivo)
        return get_fontawesome_file_icon(file_info)

    def get_context(self, request):
        """Adiciona arquivos com ícones ao contexto."""
        context = super().get_context(request)

        # Prepara uma lista de arquivos com seus ícones para o template
        arquivos_com_icone = []
        if self.arquivos:
            for block in self.arquivos:
                doc = block.value
                if doc:
                    arquivos_com_icone.append({
                        'documento': doc,
                        'icon_class': self.get_arquivo_icon(doc)
                    })
        context['arquivos_com_icone'] = arquivos_com_icone
        return context

    class Meta:
        abstract = True
