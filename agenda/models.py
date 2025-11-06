from django.db import models
from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from core.models import PageSitePadrao, PageSitePadraoIndex
from core.utils import get_parent_field
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from django.shortcuts import redirect
from wagtail.models.panels import PanelPlaceholder

from django.utils.translation import gettext_lazy as _

from blocks.agenda import CompromissoBlock


class AgendaPage(RoutablePageMixin, PageSitePadrao):
    """
    Página que representa uma agenda.
    """
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        default=""
    )
    orgao = models.CharField(
        verbose_name="Órgão",
        max_length=255,
        blank=True,
        default=""
    )
    nome_autoridade = models.CharField(
        verbose_name="Nome da Autoridade",
        max_length=255,
        blank=True,
        default=""
    )
    brasao = models.ForeignKey(
        'wagtailimages.Image',
        verbose_name="Brasão",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    local_padrao = models.CharField(
        verbose_name="Local padrão do compromisso",
        max_length=255,
        blank=False,
        null=True,
        default=""
    )
    imagem_destaque = models.ForeignKey(
        'wagtailimages.Image',
        verbose_name="Imagem destaque",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    parent_page_types = ['agenda.AgendaIndexPage']
    subpage_types = ['agenda.AgendaDoDiaPage']

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel("descricao"),
        FieldPanel("orgao"),
        FieldPanel("nome_autoridade"),
        FieldPanel("brasao"),
        FieldPanel("local_padrao"),
        FieldPanel("imagem_destaque"),
    ]

    @route(r'^dia/(?P<data>[\w-]+)/$')
    def get_agenda_do_dia(self, request, data):
        try:
            # Busca a página de agenda do dia pela data, apenas entre os filhos desta AgendaPage
            agenda_do_dia = AgendaDoDiaPage.objects.live().descendant_of(self).filter(date=data).first()
            if not agenda_do_dia:
                return JsonResponse({"error": "Agenda não encontrada para a data fornecida."}, status=404)

            # Retorna os compromissos em formato JSON
            compromissos = [
                block.value for block in agenda_do_dia.compromissos
            ]
            return JsonResponse({
                "data": data,
                "compromissos": compromissos,
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    class Meta:
        verbose_name = "Página de Agenda"

    def get_context(self, request):
        context = super().get_context(request)
        # Busca todas as AgendaDoDiaPage filhas desta AgendaPage, ordenadas por data
        datas = (
            AgendaDoDiaPage.objects.live()
            .child_of(self)
            .order_by("date")
            .values_list("date", flat=True)
        )
        # Formata as datas no padrão YYYY-MM-DD
        context["datas_agenda"] = [d.strftime("%Y-%m-%d") for d in datas]
        return context


class AgendaIndexPage(RoutablePageMixin, PageSitePadraoIndex):
    """
    Página que serve como índice para a aplicação de agenda.
    """
    parent_page_types = ['home.HomePage', 'intranet.IntranetHomePage']
    subpage_types = ['agenda.AgendaPage']

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(AgendaIndexPage, self).get_context(request)
        all_agendas = AgendaPage.objects.descendant_of(self).live().order_by("-title")
        paginator = Paginator(all_agendas, 12) # Show 12 agendas per page
        page = request.GET.get("page")
        try:
            agendas_page = paginator.page(page)
        except PageNotAnInteger:
            agendas_page = paginator.page(1)
        except EmptyPage:
            agendas_page = paginator.page(paginator.num_pages)
        
        # Adiciona a url de cada agenda
        agendas_with_url = []
        for agenda in agendas_page:
            agenda_dict = {
                "title": agenda.title,
                "url": agenda.url,
                # Adicione outros campos necessários aqui, se desejar
            }
            agendas_with_url.append(agenda_dict)

        context["agendas"] = agendas_with_url
        return context


class AgendaDoDiaPage(PageSitePadrao):
    """
    Página que representa a agenda de um único dia, contendo múltiplos compromissos.
    """
    date = models.DateField(
        verbose_name="Data da Agenda",
        unique=False,
        default=datetime.today
    )
    compromissos = StreamField(
        [("compromisso", CompromissoBlock())],
        verbose_name="Compromissos do Dia",
        blank=True,
        use_json_field=True,
    )
    nome_autoridade = models.CharField(
        verbose_name="Nome da Autoridade",
        max_length=255,
        blank=True,
        default=""
    )
    local_padrao = models.CharField(
        verbose_name="Local padrão do compromisso",
        max_length=255,
        blank=True,
        default=""
    )

    content_panels = [
        # FieldPanel("title", read_only=True),
        FieldPanel("date"),
        FieldPanel("compromissos"),
        FieldPanel("nome_autoridade"),
        FieldPanel("local_padrao"),
    ]

    promote_panels = [
        PanelPlaceholder(
            "wagtail.admin.panels.MultiFieldPanel",
            [
                [
                    "seo_title",
                    "search_description",
                ],
                _("For search engines"),
            ],
            {},
        ),
        PanelPlaceholder(
            "wagtail.admin.panels.MultiFieldPanel",
            [
                [
                    "show_in_menus",
                ],
                _("For site menus"),
            ],
            {},
        ),
    ]

    # Restringir o pai da AgendaDoDiaPage para ser apenas AgendaPage
    parent_page_types = ['agenda.AgendaPage']
    subpage_types = []  # Não pode ter filhos

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.title:
            self.title = "Agenda do Dia"

    def save(self, *args, **kwargs):
        # Inicializa campos com valor do pai se não estiverem preenchidos
        if not self.local_padrao:
            self.local_padrao = get_parent_field(self, "local_padrao")
        if not self.nome_autoridade:
            self.nome_autoridade = get_parent_field(self, "nome_autoridade")

        # Preenche nome_autoridade e local nos compromissos se estiverem vazios
        for block in self.compromissos:
            value = block.value
            if not value.get("nome_autoridade"):
                value["nome_autoridade"] = get_parent_field(self, "nome_autoridade")
            if not value.get("local"):
                value["local"] = get_parent_field(self, "local_padrao")

        super().save(*args, **kwargs)

    def serve(self, request):
        # Redireciona apenas se NÃO estiver no admin e usuário não autenticado
        if not request.user.is_authenticated and not request.path.startswith('/admin/'):
            parent = self.get_parent().specific
            agenda_url = parent.url
            redirect_url = f"{agenda_url}?data={self.date.strftime('%Y-%m-%d')}"
            return redirect(redirect_url)
        return super().serve(request)