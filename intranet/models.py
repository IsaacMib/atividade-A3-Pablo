from django.db import models
from wagtail.search import index
from django.shortcuts import redirect
from django.contrib import messages
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.fields import StreamField
from core.models import PageSitePadrao 
from wagtail import blocks


from blocks.models import (
 TituloBlock,
 AvisosListBlock,
 AcessosRapidosBlock,
 BannerComLinkBlock,
 ListaVideosBlock,
 OdometerListBlock,
 NoticiasListBlock,
 CarrosselBannersBlock,
 ServicosOnlineBlock,
 CarrosselSolucoesBlock,
 GridImagensBlock,
 ServicoOnlineItemBlock,
 AcordeonBlock,
 CustomFormBlock,
 LinhaDoTempoBlock,
 AvisosWidget,
 AcessoRapidoWidget,
)
from blocks.agenda import ListAgendaBlock 
from django.core.files.base import File 
from wagtail.blocks import RichTextBlock 
from wagtail.images.blocks import ImageChooserBlock 


INTRANET_HOME_BLOCKS = [
 ('titulo', TituloBlock()),
 ('lista_avisos', AvisosListBlock()),
 ("acessos_rapidos", AcessosRapidosBlock()),
 ('banner_com_link', BannerComLinkBlock()),
 ('lista_videos', ListaVideosBlock()),
 ("central_monitoramento", OdometerListBlock()),
 ('noticias', NoticiasListBlock()),
 ("carrossel_banners", CarrosselBannersBlock()),
 ("servicos_online", ServicosOnlineBlock()),
 ("list_agenda", ListAgendaBlock()),
 ("carrossel_solucoes", CarrosselSolucoesBlock()),
 ("programa", GridImagensBlock()),
 ("secao_informativa", AcordeonBlock()),
 ("formulario_customizado", CustomFormBlock()),
 ("servico_online_item", ServicoOnlineItemBlock()),
 ("linha_do_tempo", LinhaDoTempoBlock()),
]

# Lista de blocos disponíveis para a coluna de Widgets
INTRANET_WIDGET_BLOCKS = [
    ('titulo', TituloBlock()),
    ('widget_avisos', AvisosWidget()), # Usando o novo bloco de widget
    ("acessos_rapidos", AcessoRapidoWidget()),
    ('banner_com_link', BannerComLinkBlock()),
    # Adicione aqui outras versões de blocos otimizadas para widgets
]
#TODOGABRIEL: Compatibilizar para usar 1 home apenas e 1 base.html para o projeto.
class IntranetHomePage(PageSitePadrao):

  body = StreamField(
    INTRANET_HOME_BLOCKS,
    use_json_field=True,
    null=True,
    default=None,
    blank=True,
    verbose_name="Body"
    )

  widgets = StreamField(
    INTRANET_WIDGET_BLOCKS, 
    use_json_field=True,
    null=True,
    default=None,
    blank=True,
    verbose_name="Widgets"
    )
  
  search_fields = PageSitePadrao.search_fields + [
        index.SearchField('title', partial_match=True),
        index.SearchField('body'),
        index.FilterField('title'),
    ]

  # Painéis de conteúdo separados para abas
  content_panels = PageSitePadrao.content_panels + [
    FieldPanel("body"),
  ]

  widget_panels = [
    FieldPanel("widgets"),
  ]

  # Organiza os painéis em abas
  edit_handler = TabbedInterface([
      ObjectList(content_panels, heading='Conteúdo'),
      ObjectList(widget_panels, heading='Widgets'),
      ObjectList(PageSitePadrao.promote_panels, heading='Promover'),
      ObjectList(PageSitePadrao.settings_panels, heading='Configurações'),
  ])

  parent_page_types = ['wagtailcore.Page']

  subpage_types = [
    'noticias.NoticiasIndexPages',
    'avisos.AvisosIndexPage',
    'eventos.EventosIndexPage',
    'agenda.AgendaIndexPage',
    'intranet.IntranetPage',
    ]

  class Meta:
    verbose_name = "Página Principal da Intranet"
    verbose_name_plural = "Páginas Principais da Intranet"

  def get_context(self, request, *args, **kwargs):
    context = super().get_context(request, *args, **kwargs)
    context.update({
      "col1_blocks": self.body,
      "widget_blocks": self.widgets,
      "col1_class": "col-lg-7 col-12",
      "widget_class": "col-lg-5 col-12", 
      "is_intranet_home": True,
    })
    return context

  def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            if self._process_custom_form(request):
                return redirect(request.path)
        return super().serve(request, *args, **kwargs)

class IntranetPage(PageSitePadrao):
  body = StreamField(
    INTRANET_HOME_BLOCKS,
    use_json_field=True,
    null=True,
    default=None,
    blank=True,
    verbose_name="Conteúdo da Página"
    )
  content_panels = PageSitePadrao.content_panels + [
    FieldPanel("body"),
    ]
  parent_page_types = ['intranet.IntranetHomePage', 'intranet.IntranetPage']
  subpage_types = ['intranet.IntranetPage']
  
  class Meta:
    verbose_name = "Página de Conteúdo da Intranet"
    verbose_name_plural = "Páginas de Conteúdo da Intranet"