from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField, RichTextField
from wagtail.contrib.routable_page.models import RoutablePageMixin

from core.models import PageSitePadrao, PageSitePadraoIndex
from datetime import datetime
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .blocks import FaseEditalBlock, SITUACAO_EDITAL_CHOICES

class EditalPage(PageSitePadrao):
    tipo_publicacao = models.CharField(
        max_length=100,
        verbose_name="Tipo de Publicação",
        default="Edital",
        help_text="Ex: Edital, Chamada Pública, Aviso de Licitação."
    )
    rotulo_numero = models.CharField(
        max_length=20,
        verbose_name="Rótulo do Número",
        default="Nº", help_text="Texto que precede o número. Ex: Nº, Processo."
    )
    numero = models.CharField(max_length=50, verbose_name="Número")
    ano = models.IntegerField(verbose_name="Ano", default=datetime.now().year)
    descricao = RichTextField(
        verbose_name="Descrição da Publicação",
        help_text="Breve descrição sobre o objeto."
    )
    data_publicacao = models.DateField(
        "Data de publicação", default=datetime.today
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_EDITAL_CHOICES,
        default='aberto',
        verbose_name="Situação da Publicação"
    )

    fases_edital = StreamField(
        [("fase", FaseEditalBlock())],
        verbose_name="Fases (Ciclo de Vida)",
        help_text="Adicione as fases da publicação, como abertura, inscrições, retificações, resultados, etc.",
        use_json_field=True,
        blank=True
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('tipo_publicacao'),
            FieldPanel('rotulo_numero'),
            FieldPanel('numero'),
            FieldPanel('ano'),
            FieldPanel('situacao'),
            FieldPanel('data_publicacao'),
        ], heading="Informações Principais"),
        FieldPanel('descricao', classname="full"),
        FieldPanel('fases_edital'),
    ]
    list_display = ("title", "ano", "situacao", "live")
    list_filter = ("ano", "situacao")

    parent_page_types = ['editais.EditaisIndexPage']
    subpage_types = []

    template = "edital_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if self.fases_edital:
            context['fases_ordenadas'] = sorted(self.fases_edital, key=lambda fase: fase.value['data_fase'], reverse=True)

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
 
        # Transforma o dicionário em uma lista ordenada para paginação
        lista_de_anos = sorted(editais_por_ano.items(), key=lambda x: x[0], reverse=True)
 
        # Paginação: 10 anos por página
        paginator = Paginator(lista_de_anos, 10)
        page = request.GET.get("page")
        try:
            anos_paginados = paginator.page(page)
        except PageNotAnInteger:
            anos_paginados = paginator.page(1)
        except EmptyPage:
            anos_paginados = paginator.page(paginator.num_pages)
 
        context['anos_paginados'] = anos_paginados
        return context

    class Meta:
        verbose_name = "Página de Índice de Editais"
