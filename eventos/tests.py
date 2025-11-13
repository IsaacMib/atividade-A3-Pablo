from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.core.paginator import Page as PaginatorPage
from wagtail.models import Page, Locale
from taggit.models import Tag
from datetime import datetime

from core.utils_test import ensure_root_page
from home.models import HomePage
from eventos.models import EventosPage, EventosIndexPage, EventosPageTag


class EventosPageTestCase(TestCase):
    """Testes para o modelo EventosPage."""

    @classmethod
    def setUpTestData(cls):
        """Setup executado uma vez para toda a classe."""
        cls.root_page = ensure_root_page()
        cls.root_page.numchild = 0
        cls.root_page.save()
        cls.root_page.refresh_from_db()

        cls.locale = Locale.get_default()
        cls.factory = RequestFactory()

        # Criar HomePage
        cls.home_page = HomePage(
            title="Home Test Eventos",
            slug="home-eventos-page",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Criar EventosIndexPage
        cls.index_page = EventosIndexPage(
            title="Eventos",
            slug="eventos-page",
            introduction="Página de eventos de teste",
        )
        cls.home_page.add_child(instance=cls.index_page)
        cls.index_page.save_revision().publish()

    def setUp(self):
        """Setup executado antes de cada teste."""
        self.root_page.refresh_from_db()
        self.home_page.refresh_from_db()
        self.index_page.refresh_from_db()

    def test_criar_evento_basico(self):
        """Testa criação de evento com dados básicos."""
        evento = EventosPage(
            title="Evento de Teste",
            slug="evento-teste",
            descricao="Descrição do evento de teste",
            data_publicacao=datetime(2025, 11, 13, 10, 0),
        )
        self.index_page.add_child(instance=evento)
        evento.save_revision().publish()

        self.assertEqual(evento.title, "Evento de Teste")
        self.assertEqual(evento.descricao, "Descrição do evento de teste")
        self.assertTrue(evento.live)

    def test_validacao_titulo_maximo_50_caracteres(self):
        """Testa validação de título com mais de 50 caracteres."""
        evento = EventosPage(
            title="A" * 51,  # 51 caracteres
            slug="evento-longo",
            descricao="Teste",
        )
        self.index_page.add_child(instance=evento)

        with self.assertRaises(ValidationError) as context:
            evento.clean()

        self.assertIn("title", context.exception.message_dict)
        self.assertIn("50 caracteres", str(context.exception))

    def test_evento_com_tags(self):
        """Testa criação de evento com tags."""
        evento = EventosPage(
            title="Evento com Tags",
            slug="evento-tags",
            descricao="Evento de teste com tags",
        )
        self.index_page.add_child(instance=evento)
        evento.save()

        # Adicionar tags
        tag1 = Tag.objects.create(name="Conferência", slug="conferencia")
        tag2 = Tag.objects.create(name="Tecnologia", slug="tecnologia")
        evento.tags.add(tag1, tag2)

        self.assertEqual(evento.tags.count(), 2)
        self.assertIn(tag1, evento.tags.all())
        self.assertIn(tag2, evento.tags.all())

    def test_get_tags_com_urls(self):
        """Testa propriedade get_tags que retorna tags com URLs."""
        evento = EventosPage(
            title="Evento Test Tags",
            slug="evento-test-tags",
            descricao="Teste",
        )
        self.index_page.add_child(instance=evento)
        evento.save()

        tag = Tag.objects.create(name="Workshop", slug="workshop")
        evento.tags.add(tag)

        tags_com_url = evento.get_tags
        self.assertEqual(len(tags_com_url), 1)
        self.assertTrue(tags_com_url[0].url.endswith("tags/workshop/"))

    def test_get_ultimos_eventos(self):
        """Testa método get_ultimos_eventos."""
        # Criar múltiplos eventos
        for i in range(8):
            evento = EventosPage(
                title=f"Evento {i}",
                slug=f"evento-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=evento)
            evento.save_revision().publish()

        primeiro_evento = EventosPage.objects.first()
        ultimos = primeiro_evento.get_ultimos_eventos(quantidade=6)

        self.assertEqual(len(ultimos), 6)
        # Verifica ordenação por data_publicacao decrescente
        self.assertEqual(ultimos[0].title, "Evento 7")

    def test_get_context_inclui_ultimos_eventos(self):
        """Testa se get_context inclui ultimos_eventos."""
        evento = EventosPage(
            title="Evento Context",
            slug="evento-context",
            descricao="Teste de contexto",
        )
        self.index_page.add_child(instance=evento)
        evento.save_revision().publish()

        request = self.factory.get("/")
        context = evento.get_context(request)

        self.assertIn("ultimos_eventos", context)

    def test_parent_page_types(self):
        """Testa que EventosPage só pode ser filho de EventosIndexPage."""
        self.assertIn("EventosIndexPage", EventosPage.parent_page_types)
        self.assertEqual(len(EventosPage.parent_page_types), 1)

    def test_subpage_types_vazio(self):
        """Testa que EventosPage não permite subpáginas."""
        self.assertEqual(EventosPage.subpage_types, [])


class EventosIndexPageTestCase(TestCase):
    """Testes para o modelo EventosIndexPage."""

    @classmethod
    def setUpTestData(cls):
        """Setup executado uma vez para toda a classe."""
        cls.root_page = ensure_root_page()
        cls.root_page.numchild = 0
        cls.root_page.save()
        cls.root_page.refresh_from_db()

        cls.factory = RequestFactory()

        # Criar HomePage
        cls.home_page = HomePage(
            title="Home Index Test",
            slug="home-index-eventos",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Criar EventosIndexPage
        cls.index_page = EventosIndexPage(
            title="Eventos Index",
            slug="eventos-index-page",
            introduction="Introdução de teste",
        )
        cls.home_page.add_child(instance=cls.index_page)
        cls.index_page.save_revision().publish()

    def setUp(self):
        """Setup executado antes de cada teste."""
        self.root_page.refresh_from_db()
        self.home_page.refresh_from_db()
        self.index_page.refresh_from_db()

    def test_criar_index_page(self):
        """Testa criação de EventosIndexPage."""
        self.assertEqual(self.index_page.title, "Eventos Index")
        self.assertEqual(self.index_page.introduction, "Introdução de teste")
        self.assertTrue(self.index_page.live)

    def test_get_context_com_posts_paginados(self):
        """Testa get_context retorna posts paginados."""
        # Criar eventos
        for i in range(15):
            evento = EventosPage(
                title=f"Evento {i}",
                slug=f"evento-idx-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=evento)
            evento.save_revision().publish()

        request = self.factory.get("/eventos-index/")
        context = self.index_page.get_context(request)

        self.assertIn("posts", context)
        self.assertIsInstance(context["posts"], PaginatorPage)
        self.assertEqual(len(context["posts"]), 12)  # Padrão de 12 por página
        self.assertIsNone(context["tag"])

    def test_get_context_paginacao_pagina_2(self):
        """Testa paginação na página 2."""
        # Criar 15 eventos
        for i in range(15):
            evento = EventosPage(
                title=f"Evento Pag {i}",
                slug=f"evento-pag-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, 1, 10, i),
            )
            self.index_page.add_child(instance=evento)
            evento.save_revision().publish()

        request = self.factory.get("/eventos-index/?page=2")
        context = self.index_page.get_context(request)

        self.assertEqual(len(context["posts"]), 3)  # 15 total - 12 na página 1 = 3 na página 2

    def test_get_posts_sem_tag(self):
        """Testa get_posts sem filtro de tag."""
        # Criar eventos
        for i in range(3):
            evento = EventosPage(
                title=f"Evento GP {i}",
                slug=f"evento-gp-{i}",
                descricao=f"Descrição {i}",
            )
            self.index_page.add_child(instance=evento)
            evento.save_revision().publish()

        posts = self.index_page.get_posts()
        self.assertEqual(posts.count(), 3)

    def test_get_posts_com_tag(self):
        """Testa get_posts filtrado por tag."""
        tag = Tag.objects.create(name="Seminário", slug="seminario")

        # Criar eventos com e sem tag
        evento_com_tag = EventosPage(
            title="Evento Com Tag",
            slug="evento-com-tag",
            descricao="Com tag",
        )
        self.index_page.add_child(instance=evento_com_tag)
        evento_com_tag.save()
        evento_com_tag.tags.add(tag)

        evento_sem_tag = EventosPage(
            title="Evento Sem Tag",
            slug="evento-sem-tag",
            descricao="Sem tag",
        )
        self.index_page.add_child(instance=evento_sem_tag)
        evento_sem_tag.save()

        posts = self.index_page.get_posts(tag=tag)
        self.assertEqual(posts.count(), 1)
        self.assertEqual(posts.first().title, "Evento Com Tag")

    def test_tag_archive_route_tag_existente(self):
        """Testa rota tag_archive com tag existente."""
        tag = Tag.objects.create(name="Palestra", slug="palestra")

        evento = EventosPage(
            title="Evento Palestra",
            slug="evento-palestra",
            descricao="Evento com tag palestra",
        )
        self.index_page.add_child(instance=evento)
        evento.save_revision().publish()
        evento.tags.add(tag)

        request = self.factory.get(f"{self.index_page.url}tags/palestra/")
        response = self.index_page.tag_archive(request, tag="palestra")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Evento Palestra", response.content)

    def test_tag_archive_route_tag_inexistente(self):
        """Testa rota tag_archive com tag que não existe."""
        request = self.factory.get(f"{self.index_page.url}tags/inexistente/")
        response = self.index_page.tag_archive(request, tag="inexistente")

        # Deve redirecionar para a página index
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.index_page.url)

    def test_get_ultimos_eventos_index(self):
        """Testa método get_ultimos_eventos do índice."""
        # Criar eventos
        for i in range(8):
            evento = EventosPage(
                title=f"Evento Idx {i}",
                slug=f"evento-idx-ul-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=evento)
            evento.save_revision().publish()

        ultimos = self.index_page.get_ultimos_eventos(quantidade=6)

        self.assertEqual(len(ultimos), 6)
        # Verifica ordem decrescente por data
        self.assertEqual(ultimos[0].title, "Evento Idx 7")

    def test_parent_page_types_index(self):
        """Testa parent_page_types de EventosIndexPage."""
        self.assertIn("home.HomePage", EventosIndexPage.parent_page_types)
        self.assertIn("intranet.IntranetHomePage", EventosIndexPage.parent_page_types)

    def test_subpage_types_index(self):
        """Testa que EventosIndexPage só permite EventosPage como filho."""
        self.assertEqual(EventosIndexPage.subpage_types, ["EventosPage"])


class IntegrationEventosTestCase(TestCase):
    """Testes de integração para fluxo completo de eventos."""

    @classmethod
    def setUpTestData(cls):
        """Setup de dados compartilhados."""
        cls.root_page = ensure_root_page()
        cls.root_page.numchild = 0
        cls.root_page.save()
        cls.root_page.refresh_from_db()

        cls.factory = RequestFactory()

        # Criar HomePage
        cls.home_page = HomePage(
            title="Home Integration",
            slug="home-integ-eventos",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Criar EventosIndexPage
        cls.index_page = EventosIndexPage(
            title="Eventos Integração",
            slug="eventos-integ-test",
            introduction="Teste de integração",
        )
        cls.home_page.add_child(instance=cls.index_page)
        cls.index_page.save_revision().publish()

    def setUp(self):
        """Setup por teste."""
        self.root_page.refresh_from_db()
        self.home_page.refresh_from_db()
        self.index_page.refresh_from_db()

    def test_fluxo_completo_criar_publicar_filtrar_evento(self):
        """Teste de integração: criar → publicar → filtrar por tag."""
        # Criar evento com tags
        tag = Tag.objects.create(name="Conferência", slug="conferencia")

        evento = EventosPage(
            title="Grande Conferência 2025",
            slug="grande-conferencia-2025",
            descricao="Descrição da conferência",
            data_publicacao=datetime(2025, 12, 1, 9, 0),
        )
        self.index_page.add_child(instance=evento)
        evento.save_revision().publish()
        evento.tags.add(tag)

        # Verificar publicação
        self.assertTrue(evento.live)

        # Filtrar por tag
        posts_filtrados = self.index_page.get_posts(tag=tag)
        self.assertEqual(posts_filtrados.count(), 1)
        self.assertEqual(posts_filtrados.first().title, "Grande Conferência 2025")

        # Verificar URL da tag
        tags_com_url = evento.get_tags
        self.assertEqual(len(tags_com_url), 1)
        self.assertTrue(tags_com_url[0].url.endswith("tags/conferencia/"))

    def test_fluxo_paginacao_multiplas_paginas(self):
        """Testa fluxo de paginação com múltiplas páginas."""
        # Criar 25 eventos
        for i in range(25):
            evento = EventosPage(
                title=f"Evento Paginação {i}",
                slug=f"evento-pag-flow-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, 1, i % 24, i % 60),
            )
            self.index_page.add_child(instance=evento)
            evento.save_revision().publish()

        # Página 1
        request_p1 = self.factory.get("/eventos-integ/")
        context_p1 = self.index_page.get_context(request_p1)
        self.assertEqual(len(context_p1["posts"]), 12)

        # Página 2
        request_p2 = self.factory.get("/eventos-integ/?page=2")
        context_p2 = self.index_page.get_context(request_p2)
        self.assertEqual(len(context_p2["posts"]), 12)

        # Página 3 (restante)
        request_p3 = self.factory.get("/eventos-integ/?page=3")
        context_p3 = self.index_page.get_context(request_p3)
        self.assertEqual(len(context_p3["posts"]), 1)
