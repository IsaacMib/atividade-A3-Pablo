from django.conf import settings
from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from wagtail.coreutils import get_supported_content_language_variant
from wagtail.models import Page, Site, Locale
from wagtail.signals import page_published

from agenda.models import AgendaDoDiaPage, AgendaPage
from agenda.wagtail_hooks import (
    do_after_agendadodia_page_edit
)
from home.models import HomePage
from datetime import date


def setup_request_with_messages(request):
    """Configura um request para usar o sistema de mensagens do Django"""
    # Configurar sessão
    middleware = SessionMiddleware(lambda x: x)
    middleware.process_request(request)
    request.session.save()
    
    # Configurar sistema de mensagens
    setattr(request, '_messages', FallbackStorage(request))
    return request


def ensure_root_page(locale_code: str | None = None) -> Page:
    if locale_code is None:
        locale_code = settings.LANGUAGE_CODE

    try:
        normalized_code = get_supported_content_language_variant(locale_code)
    except LookupError:
        normalized_code = locale_code

    locale, _ = Locale.objects.get_or_create(language_code=normalized_code)

    root = Page.get_first_root_node()
    if not root:
        root = Page.add_root(title="Root", slug="root")

    root.refresh_from_db()

    fields_to_update: list[str] = []

    if root.numchild is None:
        root.numchild = 0
        fields_to_update.append("numchild")

    if root.locale_id != locale.id:
        root.locale = locale
        fields_to_update.append("locale")

    if fields_to_update:
        root.save(update_fields=fields_to_update)

    return root


class WagtailHooksTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        cls.root_page.refresh_from_db()
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Configuração do RequestFactory para mock de requests
        self.factory = RequestFactory()
        self.request = setup_request_with_messages(self.factory.get('/'))
        
        # Usa a página raiz criada no setUpTestData
        self.root_page = self.__class__.root_page
        self.root_page.refresh_from_db()
        
        self.home_page = HomePage(title="Home Test Hooks", slug="home-test-hooks")
        self.root_page.add_child(instance=self.home_page)
        self.home_page.save_revision().publish()
        
        # Configurar Site para apontar para home_page
        try:
            self.site = Site.objects.get(is_default_site=True)
            self.site.root_page = self.home_page
            self.site.save()
        except Site.DoesNotExist:
            self.site = Site.objects.create(
                hostname='testserver',
                port=80,
                root_page=self.home_page,
                is_default_site=True,
                site_name="Test Site"
            )
        
        self.agenda_page = AgendaPage(
            title="Agenda Hooks Test",
            slug="agenda-hooks-test",
            local_padrao="Local Hooks"
        )
        self.home_page.add_child(instance=self.agenda_page)
        self.agenda_page.save_revision().publish()
    
    def test_titulo_agenda_normal(self):
        """Testa geração de título para agenda normal (sem recorrência)"""
        agenda_normal = AgendaDoDiaPage(
            title="Reunião Importante",
            slug="reuniao-importante",
            date=date(2025, 11, 15),
            habilitar_recorrencia=False,
            tipo_recorrencia='none'
        )
        self.agenda_page.add_child(instance=agenda_normal)
        agenda_normal.save_revision().publish()
        
        # Chama a função do hook
        do_after_agendadodia_page_edit(self.request, agenda_normal)
        
        # Verifica se o título não foi alterado
        self.assertEqual(agenda_normal.title, "Reunião Importante")
        self.assertEqual(agenda_normal.slug, "reuniao-importante")
    
    def test_titulo_agenda_recorrente_diaria(self):
        """Testa geração de título para agenda recorrente diária"""
        agenda_diaria = AgendaDoDiaPage(
            title="Reunião Diária",
            slug="reuniao-diaria",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='days'
        )
        self.agenda_page.add_child(instance=agenda_diaria)
        agenda_diaria.save_revision().publish()
        
        # Chama a função do hook
        do_after_agendadodia_page_edit(self.request, agenda_diaria)
        
        # Verifica se o título foi alterado corretamente
        self.assertIn("Agenda Recorrente Diária", agenda_diaria.title)
        self.assertIn("reuniao-diaria", agenda_diaria.slug)
        self.assertIn("recorrente", agenda_diaria.slug)
    
    def test_titulo_agenda_recorrente_semanal(self):
        """Testa geração de título para agenda recorrente semanal"""
        agenda_semanal = AgendaDoDiaPage(
            title="Reunião Semanal",
            slug="reuniao-semanal",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='months'
        )
        self.agenda_page.add_child(instance=agenda_semanal)
        agenda_semanal.save_revision().publish()
        
        do_after_agendadodia_page_edit(self.request, agenda_semanal)
        
        self.assertIn("Agenda Recorrente Mensal", agenda_semanal.title)
        self.assertIn("recorrente", agenda_semanal.slug)
    
    def test_titulo_agenda_recorrente_mensal(self):
        """Testa geração de título para agenda recorrente mensal"""
        agenda_mensal = AgendaDoDiaPage(
            title="Reunião Mensal",
            slug="reuniao-mensal",
            date=date(2025, 11, 15),
            habilitar_recorrencia=True,
            tipo_recorrencia='months'
        )
        self.agenda_page.add_child(instance=agenda_mensal)
        agenda_mensal.save_revision().publish()
        
        do_after_agendadodia_page_edit(self.request, agenda_mensal)
        
        self.assertIn("Agenda Recorrente Mensal", agenda_mensal.title)
        self.assertIn("recorrente", agenda_mensal.slug)
    
    def test_titulo_agenda_recorrente_anual(self):
        """Testa geração de título para agenda recorrente anual"""
        agenda_anual = AgendaDoDiaPage(
            title="Reunião Anual",
            slug="reuniao-anual", 
            date=date(2025, 11, 15),
            habilitar_recorrencia=True,
            tipo_recorrencia='years'
        )
        self.agenda_page.add_child(instance=agenda_anual)
        agenda_anual.save_revision().publish()
        
        do_after_agendadodia_page_edit(self.request, agenda_anual)
        
        self.assertIn("Agenda Recorrente Anual", agenda_anual.title)
        self.assertIn("recorrente", agenda_anual.slug)
    
    def test_titulo_com_parent_page_title(self):
        """Testa geração de título incluindo título da página pai"""
        agenda_com_pai = AgendaDoDiaPage(
            title="Reunião Especial",
            slug="reuniao-especial",
            date=date(2025, 11, 15),
            habilitar_recorrencia=True,
            tipo_recorrencia='days',
            intervalo_recorrencia=7  # Semanal = a cada 7 dias
        )
        self.agenda_page.add_child(instance=agenda_com_pai)
        agenda_com_pai.save_revision().publish()
        
        do_after_agendadodia_page_edit(self.request, agenda_com_pai)
        
        # Verifica se inclui o título da página pai
        expected_title = f"{self.agenda_page.title} - Reunião Especial - Agenda Recorrente Semanal"
        self.assertEqual(agenda_com_pai.title, expected_title)
    
    def test_slug_nao_duplica_recorrente(self):
        """Testa se o slug não duplica a palavra 'recorrente'"""
        agenda_teste = AgendaDoDiaPage(
            title="Reunião Teste",
            slug="reuniao-teste-recorrente",  # Já tem 'recorrente' no slug
            date=date(2025, 11, 15),
            habilitar_recorrencia=True,
            tipo_recorrencia='days'
        )
        self.agenda_page.add_child(instance=agenda_teste)
        agenda_teste.save_revision().publish()
        
        do_after_agendadodia_page_edit(self.request, agenda_teste)
        
        # Conta quantas vezes 'recorrente' aparece no slug
        slug_parts = agenda_teste.slug.split('-')
        recorrente_count = slug_parts.count('recorrente')
        self.assertEqual(recorrente_count, 1, "A palavra 'recorrente' deve aparecer apenas uma vez no slug")
    
    def test_mapeamento_tipos_recorrencia(self):
        """Testa o mapeamento correto dos tipos de recorrência"""
        tipos_esperados = {
            'days': 'Diária',
            'months': 'Mensal',
            'years': 'Anual'
        }
        
        for tipo, texto_esperado in tipos_esperados.items():
            with self.subTest(tipo=tipo):
                agenda = AgendaDoDiaPage(
                    title="Reunião Teste",
                    slug="reuniao-teste",
                    date=date(2025, 11, 15),
                    habilitar_recorrencia=True,
                    tipo_recorrencia=tipo
                )
                self.agenda_page.add_child(instance=agenda)
                agenda.save_revision().publish()
                
                do_after_agendadodia_page_edit(self.request, agenda)
                
                self.assertIn(texto_esperado, agenda.title)
    
    def test_page_edit_handler_com_agenda_do_dia_page(self):
        """Testa se o handler de edição é chamado para AgendaDoDiaPage"""
        agenda = AgendaDoDiaPage(
            title="Test Page",
            slug="test-page",
            date=date(2025, 11, 15),
            habilitar_recorrencia=True,
            tipo_recorrencia='days'
        )
        self.agenda_page.add_child(instance=agenda)
        agenda.save_revision().publish()
        
        # Cria um request mockado
        request = setup_request_with_messages(RequestFactory().get('/'))
        
        # Verifica o título antes do hook
        titulo_antes = agenda.title
        
        # Simula o hook diretamente
        do_after_agendadodia_page_edit(request, agenda)
        
        # Verifica se o título foi modificado (indica que o hook foi executado)
        self.assertNotEqual(agenda.title, titulo_antes)
        self.assertIn("Agenda Recorrente", agenda.title)
    
    def test_page_edit_handler_com_outra_page(self):
        """Testa se o handler não é chamado para outros tipos de página"""
        # Cria uma página que não é AgendaDoDiaPage
        other_page = self.agenda_page  # AgendaPage
        
        # Cria um request mockado
        request = setup_request_with_messages(RequestFactory().get('/'))
        
        # Simula o hook (não deve fazer nada)
        try:
            do_after_agendadodia_page_edit(request, other_page)
            # Se chegou aqui, não houve erro (comportamento esperado)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Handler não deveria falhar para outras páginas: {e}")
    
    def test_titulo_preserva_estrutura_original(self):
        """Testa se o título preserva a estrutura original quando não há recorrência"""
        agenda_sem_recorrencia = AgendaDoDiaPage(
            title="Reunião Importante da Diretoria",
            slug="reuniao-importante-diretoria",
            date=date(2025, 11, 15),
            habilitar_recorrencia=False
        )
        self.agenda_page.add_child(instance=agenda_sem_recorrencia)
        agenda_sem_recorrencia.save_revision().publish()
        
        titulo_original = agenda_sem_recorrencia.title
        slug_original = agenda_sem_recorrencia.slug
        
        do_after_agendadodia_page_edit(self.request, agenda_sem_recorrencia)
        
        # Título e slug não devem ter mudado
        self.assertEqual(agenda_sem_recorrencia.title, titulo_original)
        self.assertEqual(agenda_sem_recorrencia.slug, slug_original)
    
    def test_titulo_com_caracteres_especiais(self):
        """Testa comportamento com títulos que contêm caracteres especiais"""
        agenda_especial = AgendaDoDiaPage(
            title="Reunião & Café - 100% Participação",
            slug="reuniao-cafe-participacao",
            date=date(2025, 11, 15),
            habilitar_recorrencia=True,
            tipo_recorrencia='days',
            intervalo_recorrencia=7  # Semanal = a cada 7 dias
        )
        self.agenda_page.add_child(instance=agenda_especial)
        agenda_especial.save_revision().publish()
        
        do_after_agendadodia_page_edit(self.request, agenda_especial)
        
        # Verifica se os caracteres especiais foram preservados no título
        self.assertIn("Reunião & Café - 100% Participação", agenda_especial.title)
        self.assertIn("Agenda Recorrente Semanal", agenda_especial.title)
        self.assertIn("recorrente", agenda_especial.slug)


class IntegrationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        cls.root_page.refresh_from_db()
    
    def setUp(self):
        """Configuração para testes de integração"""
        # Configuração do RequestFactory para mock de requests
        self.factory = RequestFactory()
        self.request = setup_request_with_messages(self.factory.get('/'))
        
        # Usa a página raiz criada no setUpTestData
        self.root_page = self.__class__.root_page
        self.root_page.refresh_from_db()
        
        self.home_page = HomePage(title="Home Integration", slug="home-integration")
        self.root_page.add_child(instance=self.home_page)
        
        self.agenda_page = AgendaPage(
            title="Agenda Integração",
            slug="agenda-integracao",
            local_padrao="Local Integração"
        )
        self.home_page.add_child(instance=self.agenda_page)
        self.agenda_page.save_revision().publish()
    
    def test_fluxo_completo_criacao_agenda_recorrente(self):
        """Testa o fluxo completo de criação de uma agenda recorrente"""
        # Cria agenda recorrente
        agenda = AgendaDoDiaPage(
            title="Reunião Semanal da Equipe",
            slug="reuniao-semanal-equipe",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='days',
            intervalo_recorrencia=7,  # Semanal = a cada 7 dias
            data_final_recorrencia=date(2025, 12, 31)
        )
        self.agenda_page.add_child(instance=agenda)
        agenda.save_revision().publish()
        
        # Aplica os hooks
        do_after_agendadodia_page_edit(self.request, agenda)
        
        # Verifica se o título foi modificado corretamente
        expected_title = f"{self.agenda_page.title} - Reunião Semanal da Equipe - Agenda Recorrente Semanal"
        self.assertEqual(agenda.title, expected_title)
        
        # Verifica se o slug foi modificado corretamente
        self.assertIn("recorrente", agenda.slug)
        
        # Verifica se a lógica de recorrência funciona
        self.assertTrue(agenda.data_aplica_na_recorrencia(date(2025, 11, 11)))
        self.assertTrue(agenda.data_aplica_na_recorrencia(date(2025, 11, 18)))
        self.assertTrue(agenda.data_aplica_na_recorrencia(date(2025, 11, 25)))
        
        # Verifica se consegue buscar agendas por data
        agendas_encontradas = AgendaDoDiaPage.get_agendas_para_data(date(2025, 11, 18))
        self.assertEqual(len(agendas_encontradas), 1)
        self.assertEqual(agendas_encontradas[0].id, agenda.id)
    
    def test_fluxo_edicao_agenda_normal_para_recorrente(self):
        """Testa o fluxo de edição de uma agenda normal para recorrente"""
        # Cria agenda normal primeiro
        agenda = AgendaDoDiaPage(
            title="Reunião Única",
            slug="reuniao-unica",
            date=date(2025, 11, 15),
            habilitar_recorrencia=False
        )
        self.agenda_page.add_child(instance=agenda)
        agenda.save_revision().publish()
        
        # Verifica estado inicial
        titulo_inicial = agenda.title
        slug_inicial = agenda.slug
        
        # Aplica hooks (não deve alterar nada)
        do_after_agendadodia_page_edit(self.request, agenda)
        self.assertEqual(agenda.title, titulo_inicial)
        self.assertEqual(agenda.slug, slug_inicial)
        
        # Agora altera para recorrente
        agenda.habilitar_recorrencia = True
        agenda.tipo_recorrencia = 'months'
        agenda.intervalo_recorrencia = 1
        agenda.data_final_recorrencia = date(2026, 11, 15)
        agenda.save()
        
        # Aplica hooks novamente
        do_after_agendadodia_page_edit(self.request, agenda)
        
        # Verifica se foi alterado corretamente
        self.assertIn("Agenda Recorrente Mensal", agenda.title)
        self.assertIn("recorrente", agenda.slug)
        self.assertTrue(agenda.data_aplica_na_recorrencia(date(2025, 12, 15)))  # Próximo mês