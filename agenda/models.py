from django.db import models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

    parent_page_types = ['agenda.AgendaIndexPage']
    subpage_types = ['agenda.AgendaDoDiaPage']

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel("orgao"),
        FieldPanel("nome_autoridade"),
        FieldPanel("brasao"),
        FieldPanel("local_padrao"),
        FieldPanel("imagem_destaque"),
    ]

    # Remove imagem_destaque do promote_panels (já está no content_panels)
    promote_panels = [
        panel for panel in PageSitePadrao.promote_panels 
        if not (hasattr(panel, 'field_name') and panel.field_name == 'imagem_destaque')
    ]

    @route(r'^dia/(?P<data>[\w-]+)/$')
    def get_agenda_do_dia(self, request, data):
        try:
            from datetime import datetime
            # Converte a string da data para objeto date
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            
            # Busca agendas que se aplicam a esta data (considerando recorrências)
            agendas = AgendaDoDiaPage.get_agendas_para_data(data_obj, parent_page=self)
            
            if not agendas:
                return JsonResponse({"error": "Agenda não encontrada para a data fornecida."}, status=404)

            # Retorna os compromissos de todas as agendas que se aplicam a esta data
            todos_compromissos = []
            for agenda in agendas:
                compromissos = [
                    block.value for block in agenda.compromissos
                ]
                todos_compromissos.extend(compromissos)
            
            return JsonResponse({
                "data": data,
                "compromissos": todos_compromissos,
                "total_agendas": len(agendas)
            })
        except ValueError:
            return JsonResponse({"error": "Formato de data inválido. Use YYYY-MM-DD."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @route(r'^datas-periodo/$')
    def get_datas_periodo(self, request):
        """
        API endpoint que retorna todas as datas de recorrência em um período específico
        para todas as agendas filhas desta AgendaPage.
        Calcula períodos inteligentes baseados no tipo de recorrência.
        Suporta tanto GET quanto POST.
        """
        try:
            from datetime import datetime, timedelta
            from dateutil.relativedelta import relativedelta
            
            # Verifica método HTTP - só permite GET e POST
            if request.method not in ['GET', 'POST']:
                return JsonResponse({"error": f"Método {request.method} não suportado."}, status=405)
            
            # Suporta tanto GET quanto POST
            if request.method == 'POST':
                start_str = request.POST.get('start')
                end_str = request.POST.get('end')
            else:
                start_str = request.GET.get('start')
                end_str = request.GET.get('end')
            
            if not start_str or not end_str:
                return JsonResponse({"error": "Parâmetros 'start' e 'end' são obrigatórios."}, status=400)
            
            # Converte as strings para objetos date
            base_start = datetime.strptime(start_str, '%Y-%m-%d').date()
            base_end = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            # Validação adicional: data final não pode ser anterior à inicial
            if base_end < base_start:
                return JsonResponse({"error": "Data final não pode ser anterior à data inicial."}, status=400)
            
            # Busca todas as AgendaDoDiaPage filhas desta AgendaPage
            agendas = AgendaDoDiaPage.objects.live().child_of(self).order_by("date")
            
            # Calcula período expandido baseado nos tipos de recorrência encontrados
            todas_datas = set()
            periodo_maximo = base_end
            
            for agenda in agendas:
                if agenda.habilitar_recorrencia and agenda.tipo_recorrencia != 'none':
                    # Calcula período expandido baseado no tipo de recorrência
                    if agenda.tipo_recorrencia == 'days':
                        # Para diária: expande 6 meses (180 dias ÷ 1 dia = ~180 ocorrências)
                        periodo_agenda = base_end + relativedelta(months=6)
                    elif agenda.tipo_recorrencia == 'months':
                        # Para mensal: expande 24 meses (24 ocorrências)
                        periodo_agenda = base_end + relativedelta(months=24)
                    elif agenda.tipo_recorrencia == 'years':
                        # Para anual: expande 10 anos (10 ocorrências)
                        periodo_agenda = base_end + relativedelta(years=10)
                    else:
                        periodo_agenda = base_end
                    
                    # Atualiza o período máximo
                    if periodo_agenda > periodo_maximo:
                        periodo_maximo = periodo_agenda
                    
                    # Calcula as datas de recorrência para o período expandido
                    data_atual = base_start
                    while data_atual <= periodo_agenda and (not agenda.data_final_recorrencia or data_atual <= agenda.data_final_recorrencia):
                        if agenda.data_aplica_na_recorrencia(data_atual):
                            todas_datas.add(data_atual)
                        data_atual += timedelta(days=1)
                else:
                    # Para agendas normais, verifica se está no período base
                    if base_start <= agenda.date <= base_end:
                        todas_datas.add(agenda.date)
            
            # Formata as datas para string
            datas_formatadas = [d.strftime("%Y-%m-%d") for d in sorted(todas_datas)]
            
            return JsonResponse({
                "datas": datas_formatadas,
                "periodo": {
                    "inicio": start_str,
                    "fim": end_str,
                    "expandido_ate": periodo_maximo.strftime("%Y-%m-%d")
                },
                "total": len(datas_formatadas)
            })
        except ValueError as e:
            return JsonResponse({"error": f"Formato de data inválido: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    class Meta:
        verbose_name = "Página de Agenda"

    def get_context(self, request):
        context = super().get_context(request)
        
        # Busca todas as AgendaDoDiaPage filhas desta AgendaPage
        agendas = AgendaDoDiaPage.objects.live().child_of(self).order_by("date")
        
        # Coleta todas as datas (incluindo recorrências)
        todas_datas = set()
        
        for agenda in agendas:
            if agenda.habilitar_recorrencia and agenda.tipo_recorrencia != 'none':
                # Para agendas recorrentes, pega as próximas 50 datas
                datas_recorrencia = agenda.get_proximas_datas_recorrencia(limite=50)
                todas_datas.update(datas_recorrencia)
            else:
                # Para agendas normais, apenas a data da agenda
                todas_datas.add(agenda.date)
        
        # Ordena e formata as datas
        datas_ordenadas = sorted(todas_datas)
        context["datas_agenda"] = [d.strftime("%Y-%m-%d") for d in datas_ordenadas]
        
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


class AgendaDoDiaPage(RoutablePageMixin, PageSitePadrao):
    """
    Página que representa a agenda de um único dia, contendo múltiplos compromissos.
    """
    RECORRENCIA_CHOICES = [
        ('none', 'Sem recorrência'),
        ('days', 'Recorrência por dias'),
        ('months', 'Recorrência por meses'),
        ('years', 'Recorrência por anos'),
    ]

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
    tipo_recorrencia = models.CharField(
        verbose_name="Tipo de recorrência",
        max_length=10,
        choices=RECORRENCIA_CHOICES,
        default='none'
    )
    intervalo_recorrencia = models.PositiveIntegerField(
        verbose_name="Intervalo de recorrência",
        default=1,
        help_text="Quantidade de dias/meses/anos entre cada ocorrência"
    )
    data_final_recorrencia = models.DateField(
        verbose_name="Data final da recorrência",
        null=True,
        blank=True,
        help_text="Deixe em branco se não houver data final definida"
    )
    habilitar_recorrencia = models.BooleanField(
        verbose_name="Habilitar recorrência",
        default=False,
        help_text="Marque para ativar a recorrência para este compromisso"
    )

    content_panels = [
        # FieldPanel("title", read_only=True),
        FieldPanel("date"),
        FieldPanel("compromissos"),
        FieldPanel("nome_autoridade"),
        FieldPanel("local_padrao"),
        FieldPanel("habilitar_recorrencia"),
        FieldPanel("tipo_recorrencia"),
        FieldPanel("intervalo_recorrencia"),
        FieldPanel("data_final_recorrencia"),
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

    def clean(self):
        super().clean()
        if self.habilitar_recorrencia and self.data_final_recorrencia and self.data_final_recorrencia < self.date:
            raise ValidationError({
                'data_final_recorrencia': 'A data final da recorrência deve ser posterior à data da agenda.'
            })

    def data_aplica_na_recorrencia(self, data_consulta):
        """
        Verifica se uma data específica se aplica a esta agenda baseada na recorrência.
        """
        if not self.habilitar_recorrencia or self.tipo_recorrencia == 'none':
            return data_consulta == self.date
        
        # Verifica se a data está dentro do período válido
        if data_consulta < self.date:
            return False
            
        if self.data_final_recorrencia and data_consulta > self.data_final_recorrencia:
            return False
        
        # Calcula se a data consulta está em um intervalo válido da recorrência
        delta = data_consulta - self.date
        
        if self.tipo_recorrencia == 'days':
            return delta.days % self.intervalo_recorrencia == 0
        elif self.tipo_recorrencia == 'months':
            # Para meses, vamos verificar se a diferença em meses é múltipla do intervalo
            months_diff = (data_consulta.year - self.date.year) * 12 + (data_consulta.month - self.date.month)
            return months_diff % self.intervalo_recorrencia == 0 and data_consulta.day == self.date.day
        elif self.tipo_recorrencia == 'years':
            # Para anos, verificamos se a diferença em anos é múltipla do intervalo
            years_diff = data_consulta.year - self.date.year
            return (years_diff % self.intervalo_recorrencia == 0 and 
                    data_consulta.month == self.date.month and 
                    data_consulta.day == self.date.day)
        
        return False

    def get_proximas_datas_recorrencia(self, data_inicio=None, limite=10):
        """
        Retorna as datas de recorrência anteriores e posteriores a partir de uma data específica.
        Se limite=10, retorna 10 datas anteriores + 10 datas posteriores = 20 datas total.
        """
        if not self.habilitar_recorrencia or self.tipo_recorrencia == 'none':
            return [self.date] if not data_inicio or self.date >= data_inicio else []
        
        if data_inicio is None:
            data_inicio = datetime.now().date()
        
        todas_datas = []
        
        # Primeiro, coleta datas anteriores à data_inicio
        datas_anteriores = []
        data_atual = data_inicio
        
        # Encontra uma data válida anterior ou igual à data_inicio
        while data_atual >= self.date and len(datas_anteriores) == 0:
            if self.data_aplica_na_recorrencia(data_atual):
                break
            data_atual = data_atual - timedelta(days=1)
        
        # Se encontrou uma data válida, coleta as anteriores
        if self.data_aplica_na_recorrencia(data_atual):
            contador_anteriores = 0
            while contador_anteriores < limite and data_atual >= self.date:
                if self.data_aplica_na_recorrencia(data_atual):
                    datas_anteriores.insert(0, data_atual)  # Insere no início para manter ordem
                    contador_anteriores += 1
                
                # Retrocede baseado no tipo de recorrência
                if self.tipo_recorrencia == 'days':
                    data_atual = data_atual - timedelta(days=self.intervalo_recorrencia)
                elif self.tipo_recorrencia == 'months':
                    data_atual = data_atual - relativedelta(months=self.intervalo_recorrencia)
                elif self.tipo_recorrencia == 'years':
                    data_atual = data_atual - relativedelta(years=self.intervalo_recorrencia)
                
                # Proteção contra loop infinito
                if data_atual < datetime(1900, 1, 1).date():
                    break
        
        # Agora coleta datas posteriores à data_inicio
        datas_posteriores = []
        data_atual = data_inicio
        
        # Encontra a próxima data válida a partir da data_inicio
        tentativas = 0
        while not self.data_aplica_na_recorrencia(data_atual) and tentativas < limite * 5:
            data_atual = data_atual + timedelta(days=1)
            tentativas += 1
        
        # Coleta as datas posteriores
        contador_posteriores = 0
        while contador_posteriores < limite:
            if self.data_aplica_na_recorrencia(data_atual):
                if not self.data_final_recorrencia or data_atual <= self.data_final_recorrencia:
                    datas_posteriores.append(data_atual)
                    contador_posteriores += 1
                else:
                    break
            
            # Avança para a próxima data baseada no tipo de recorrência
            if self.tipo_recorrencia == 'days':
                data_atual = data_atual + timedelta(days=self.intervalo_recorrencia)
            elif self.tipo_recorrencia == 'months':
                data_atual = data_atual + relativedelta(months=self.intervalo_recorrencia)
            elif self.tipo_recorrencia == 'years':
                data_atual = data_atual + relativedelta(years=self.intervalo_recorrencia)
            
            # Proteção contra loop infinito
            if data_atual > datetime(2050, 12, 31).date():
                break
        
        # Combina as listas: anteriores + posteriores
        todas_datas = datas_anteriores + datas_posteriores
        
        return todas_datas

    @classmethod
    def get_agendas_para_data(cls, data_consulta, parent_page=None):
        """
        Retorna todas as agendas que se aplicam a uma data específica,
        considerando recorrências.
        """
        agendas = []
        
        # Query base
        queryset = cls.objects.live()
        if parent_page:
            queryset = queryset.child_of(parent_page)
        
        # Busca agendas que podem se aplicar à data
        for agenda in queryset:
            if agenda.data_aplica_na_recorrencia(data_consulta):
                agendas.append(agenda)
        
        return agendas

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

    def serve(self, request, *args, **kwargs):
        # Redireciona apenas se NÃO estiver no admin e usuário não autenticado
        if not request.user.is_authenticated and not request.path.startswith('/admin/'):
            parent = self.get_parent().specific
            agenda_url = parent.url
            redirect_url = f"{agenda_url}?data={self.date.strftime('%Y-%m-%d')}"
            return redirect(redirect_url)
        return super().serve(request, *args, **kwargs)

    @route(r'^datas-periodo/$')
    def get_datas_periodo(self, request):
        """
        API endpoint que retorna todas as datas de recorrência em um período específico
        Suporta tanto GET quanto POST.
        """
        try:
            from datetime import datetime, timedelta
            
            # Verifica método HTTP - só permite GET e POST
            if request.method not in ['GET', 'POST']:
                return JsonResponse({"error": f"Método {request.method} não suportado."}, status=405)
            
            # Suporta tanto GET quanto POST
            if request.method == 'POST':
                start_str = request.POST.get('start')
                end_str = request.POST.get('end')
            else:
                start_str = request.GET.get('start')
                end_str = request.GET.get('end')
            
            if not start_str or not end_str:
                return JsonResponse({"error": "Parâmetros 'start' e 'end' são obrigatórios."}, status=400)
            
            # Converte as strings para objetos date
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            # Validação adicional: data final não pode ser anterior à inicial
            if end_date < start_date:
                return JsonResponse({"error": "Data final não pode ser anterior à data inicial."}, status=400)
            
            # Para uma AgendaDoDiaPage específica, verifica se ela se aplica no período
            todas_datas = set()
            
            if self.habilitar_recorrencia and self.tipo_recorrencia != 'none':
                # Para agendas recorrentes, calcula datas no período
                data_atual = start_date
                while data_atual <= end_date:
                    if self.data_aplica_na_recorrencia(data_atual):
                        todas_datas.add(data_atual)
                    data_atual += timedelta(days=1)
            else:
                # Para agendas normais, verifica se está no período
                if start_date <= self.date <= end_date:
                    todas_datas.add(self.date)
            
            # Formata as datas para string
            datas_formatadas = [d.strftime("%Y-%m-%d") for d in sorted(todas_datas)]
            
            return JsonResponse({
                "datas": datas_formatadas,
                "periodo": {
                    "inicio": start_str,
                    "fim": end_str
                },
                "agenda_id": self.id,
                "titulo": self.title,
                "tipo_recorrencia": self.tipo_recorrencia,
                "tem_recorrencia": self.habilitar_recorrencia and self.tipo_recorrencia != 'none'
            })
        except ValueError as e:
            return JsonResponse({"error": f"Formato de data inválido: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)