from wagtail.search import index
from django.db import models
from core.models import PageSitePadrao
from django.shortcuts import redirect
from django.contrib import messages
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from blocks.models import (
  AcessosRapidosBlock,
  BannerComLinkBlock,
  ListaVideosBlock,
  OdometerListBlock,
  CarrosselBannersBlock,
  ServicosOnlineBlock,
  TituloBlock,
  NoticiasListBlock,
  CarrosselSolucoesBlock,
  AvisosListBlock,
  GridImagensBlock,
  ServicoOnlineItemBlock,
  AcordeonBlock,
  CustomFormBlock,
  LinhaDoTempoBlock
)


from blocks.agenda import ListAgendaBlock

class HomePage(PageSitePadrao):
    body = StreamField(
        [
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
        ],
        use_json_field=True,
        null=True,
        default=None,
        blank=True,
    )

    search_fields = PageSitePadrao.search_fields + [
        index.SearchField('title', partial_match=True),
        index.SearchField('body'),
        index.FilterField('title'),
    ]
    
    content_panels = PageSitePadrao.content_panels + [
        FieldPanel("body"),
    ]

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            form_block = next((block for block in self.body if isinstance(block.block, CustomFormBlock)), None)

            if form_block:
                form = form_block.block.get_context(form_block.value, parent_context={'request': request})['form']
                bound_form = type(form)(request.POST, initial=form.initial)

                if bound_form.is_valid():
                    from blocks.models import FormularioSubmissao
                    cleaned_data = bound_form.cleaned_data.copy()
                    nome_completo = cleaned_data.pop('nome_completo', '')
                    titulo = cleaned_data.pop('titulo', '')

                    FormularioSubmissao.objects.create(
                        nome_completo=nome_completo,
                        titulo=titulo,
                        dados_adicionais=cleaned_data,
                        pagina=self,
                        usuario=request.user if request.user.is_authenticated else None
                    )
                    messages.success(request, "Formulário Enviado Com Sucesso!")
                    return redirect(request.path)
                else:
                    messages.error(request, "Ocorreu um erro. Por favor, verifique os campos do formulário.")

        return super().serve(request, *args, **kwargs)
