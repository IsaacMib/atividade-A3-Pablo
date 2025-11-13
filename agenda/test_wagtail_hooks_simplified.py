from django.conf import settings
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from agenda.models import AgendaDoDiaPage, AgendaPage
from agenda.wagtail_hooks import do_after_agendadodia_page_edit
from home.models import HomePage
from wagtail.models import Page, Site, Locale
from core.utils_test import ensure_root_page
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


class WagtailHooksSimplifiedTestCase(TestCase):
    """Testes simplificados para wagtail hooks"""

    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
    
    def setUp(self):
        """Configuração básica para testes"""
        self.factory = RequestFactory()
        self.request = setup_request_with_messages(self.factory.get('/'))
        
        # Usa a página raiz criada no setUpTestData
        self.root_page = self.__class__.root_page
        self.root_page.refresh_from_db()
        
        # Configuração do Site
        Site.objects.filter(is_default_site=True).delete()
        Site.objects.create(
            hostname='testserver',
            port=80,
            root_page=self.root_page,
            is_default_site=True,
            site_name='Test Site'
        )
        
        # HomePage
        self.home_page = HomePage(title="Home", slug="home-test")
        self.root_page.add_child(instance=self.home_page)
        self.home_page.save_revision().publish()
        
        # AgendaPage
        self.agenda_page = AgendaPage(
            title="Agenda Principal",
            slug="agenda-principal",
            local_padrao="Local Teste"  # Campo obrigatório
        )
        self.home_page.add_child(instance=self.agenda_page)
        self.agenda_page.save_revision().publish()

    def test_hook_executa_sem_erros(self):
        """Testa que o hook executa sem erros para AgendaDoDiaPage"""
        agenda = AgendaDoDiaPage(
            title="Teste Hook",
            slug="teste-hook",
            date=date(2025, 11, 11),
            habilitar_recorrencia=False
        )
        self.agenda_page.add_child(instance=agenda)
        agenda.save_revision().publish()
        
        # Testa que o hook não gera erros
        try:
            do_after_agendadodia_page_edit(self.request, agenda)
            self.assertTrue(True)  # Sucesso se chegou aqui
        except Exception as e:
            self.fail(f"Hook não deveria gerar erro: {e}")

    def test_hook_com_recorrencia(self):
        """Testa hook com agenda recorrente"""
        agenda_recorrente = AgendaDoDiaPage(
            title="Teste Recorrente",
            slug="teste-recorrente",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='days'
        )
        self.agenda_page.add_child(instance=agenda_recorrente)
        agenda_recorrente.save_revision().publish()
        
        # Testa que o hook não gera erros
        try:
            do_after_agendadodia_page_edit(self.request, agenda_recorrente)
            self.assertTrue(True)  # Sucesso se chegou aqui
        except Exception as e:
            self.fail(f"Hook com recorrência não deveria gerar erro: {e}")

    def test_hook_ignora_outros_tipos_pagina(self):
        """Testa que o hook ignora outros tipos de página"""
        try:
            do_after_agendadodia_page_edit(self.request, self.agenda_page)
            self.assertTrue(True)  # Sucesso se chegou aqui
        except Exception as e:
            self.fail(f"Hook não deveria gerar erro para outras páginas: {e}")

    def test_tipos_recorrencia_validos(self):
        """Testa que os tipos de recorrência válidos funcionam"""
        tipos_validos = ['days', 'months', 'years']
        
        for tipo in tipos_validos:
            with self.subTest(tipo=tipo):
                agenda = AgendaDoDiaPage(
                    title=f"Agenda {tipo}",
                    slug=f"agenda-{tipo}",
                    date=date(2025, 11, 11),
                    habilitar_recorrencia=True,
                    tipo_recorrencia=tipo
                )
                self.agenda_page.add_child(instance=agenda)
                agenda.save_revision().publish()
                
                try:
                    do_after_agendadodia_page_edit(self.request, agenda)
                    self.assertTrue(True)  # Sucesso se chegou aqui
                except Exception as e:
                    self.fail(f"Hook com tipo {tipo} não deveria gerar erro: {e}")