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
  content_panels = [
    FieldPanel("title"), # Adiciona o campo de título aqui
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
            form_block = next((block for block in self.body if isinstance(block.block, CustomFormBlock)), None)

            if form_block:
                form = form_block.block.get_context(form_block.value, parent_context={'request': request})['form']
                form_kwargs = {
                    'show_recaptcha': getattr(form, 'show_recaptcha', False),
                    'recaptcha_secret_key': getattr(form, 'recaptcha_secret_key', None),
                    'fields_config': form.fields_config if hasattr(form, 'fields_config') else None,
                    'initial': form.initial if hasattr(form, 'initial') else {},
                    'request': request,
                }
                bound_form = type(form)(request.POST, request.FILES, **form_kwargs)

                if bound_form.is_valid():
                    from blocks.models import FormularioSubmissao, ArquivoSubmetido
                    from django.core.files.base import File
                    field_map = {}
                    if hasattr(bound_form, 'fields_config') and bound_form.fields_config:
                        for i, block in enumerate(bound_form.fields_config):
                            field_name = f"custom_field_{i}_{block.block_type}"
                            field_label = block.value.get('label', field_name)
                            field_map[field_name] = field_label

                    cleaned_data = bound_form.cleaned_data.copy()
                    arquivos_para_salvar = {}
                    dados_adicionais_serializaveis = {}

                    for key, value in cleaned_data.items():
                        if isinstance(value, File):
                            arquivos_para_salvar[key] = value
                        else:
                            dados_adicionais_serializaveis[field_map.get(key, key)] = value

                    nome_completo = cleaned_data.pop('nome_completo', '')
                    titulo = cleaned_data.pop('titulo', '')                    

                    submissao = FormularioSubmissao.objects.create(
                        nome_completo=nome_completo,
                        titulo=titulo,
                        dados_adicionais={k: v for k, v in dados_adicionais_serializaveis.items() if k not in ['nome_completo', 'titulo', 'g-recaptcha-response']},
                        pagina=self,
                        usuario=request.user if request.user.is_authenticated else None
                    )
                    for nome_campo, arquivo in arquivos_para_salvar.items():
                        ArquivoSubmetido.objects.create(submissao=submissao, nome_campo=nome_campo, arquivo=arquivo)

                    messages.success(request, "Formulário Enviado Com Sucesso!")
                    return redirect(request.path)
                else:
                    messages.error(request, "Ocorreu um erro. Por favor, verifique os campos do formulário.")
                    setattr(request, '_form_errors', bound_form)
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