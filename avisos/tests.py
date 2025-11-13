from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.core.paginator import Page as PaginatorPage
from wagtail.models import Page, Locale
from wagtail.images.tests.utils import get_test_image_file
from wagtail.images import get_image_model
from taggit.models import Tag
from datetime import datetime

from core.utils_test import ensure_root_page
from home.models import HomePage
from avisos.models import AvisosPage, AvisosIndexPage, AvisosPageTag

Image = get_image_model()


class AvisosPageTestCase(TestCase):
    """Testes para o modelo AvisosPage."""

    @classmethod
    def setUpTestData(cls):
        """Setup executado uma vez para toda a classe."""
        cls.root_page = ensure_root_page()
        cls.root_page.numchild = 0
        cls.root_page.save()
        cls.root_page.refresh_from_db()

        cls.locale = Locale.get_default()
        cls.factory = RequestFactory()

        # Criar imagem de teste
        cls.test_image = Image.objects.create(
            title="Test Image",
            file=get_test_image_file(),
        )

        # Criar HomePage
        cls.home_page = HomePage(
            title="Home Test Avisos",
            slug="home-avisos-page",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Criar AvisosIndexPage
        cls.index_page = AvisosIndexPage(
            title="Avisos",
            slug="avisos-page",
            introduction="Todos os avisos",
        )
        cls.home_page.add_child(instance=cls.index_page)
        cls.index_page.save_revision().publish()

    def setUp(self):
        """Setup executado antes de cada teste."""
        self.root_page.refresh_from_db()
        self.home_page.refresh_from_db()
        self.index_page.refresh_from_db()

    def test_criar_aviso_basico(self):
        """Testa criação de aviso com dados básicos."""
        aviso = AvisosPage(
            title="Aviso de Teste",
            slug="aviso-teste",
            descricao="Descrição do aviso de teste",
            data_publicacao=datetime(2025, 11, 13, 10, 0),
            destaque=False,
        )
        self.index_page.add_child(instance=aviso)
        aviso.save_revision().publish()

        self.assertEqual(aviso.title, "Aviso de Teste")
        self.assertEqual(aviso.descricao, "Descrição do aviso de teste")
        self.assertFalse(aviso.destaque)
        self.assertTrue(aviso.live)

    def test_validacao_titulo_maximo_100_caracteres(self):
        """Testa validação de título com mais de 100 caracteres."""
        aviso = AvisosPage(
            title="A" * 101,  # 101 caracteres
            slug="aviso-longo",
            descricao="Teste",
        )
        self.index_page.add_child(instance=aviso)

        with self.assertRaises(ValidationError) as context:
            aviso.clean()

        self.assertIn("title", context.exception.message_dict)
        self.assertIn("100 caracteres", str(context.exception))

    def test_aviso_em_destaque(self):
        """Testa criação de aviso em destaque."""
        aviso = AvisosPage(
            title="Aviso Importante",
            slug="aviso-importante",
            descricao="Aviso em destaque",
            destaque=True,
        )
        self.index_page.add_child(instance=aviso)
        aviso.save_revision().publish()

        self.assertTrue(aviso.destaque)

    def test_aviso_com_tags(self):
        """Testa criação de aviso com tags."""
        aviso = AvisosPage(
            title="Aviso com Tags",
            slug="aviso-tags",
            descricao="Aviso de teste com tags",
        )
        self.index_page.add_child(instance=aviso)
        aviso.save()

        # Adicionar tags
        tag1 = Tag.objects.create(name="Urgente", slug="urgente")
        tag2 = Tag.objects.create(name="Comunicado", slug="comunicado")
        aviso.tags.add(tag1, tag2)

        self.assertEqual(aviso.tags.count(), 2)
        self.assertIn(tag1, aviso.tags.all())
        self.assertIn(tag2, aviso.tags.all())

    def test_get_tags_com_urls(self):
        """Testa propriedade get_tags que retorna tags com URLs."""
        aviso = AvisosPage(
            title="Aviso Test Tags",
            slug="aviso-test-tags",
            descricao="Teste",
        )
        self.index_page.add_child(instance=aviso)
        aviso.save()

        tag = Tag.objects.create(name="Importante", slug="importante")
        aviso.tags.add(tag)

        tags_com_url = aviso.get_tags
        self.assertEqual(len(tags_com_url), 1)
        self.assertTrue(tags_com_url[0].url.endswith("tags/importante/"))

    def test_aviso_com_slideshow_ativado(self):
        """Testa aviso com slideshow de imagens ativado."""
        aviso = AvisosPage(
            title="Aviso Slideshow",
            slug="aviso-slideshow",
            descricao="Teste slideshow",
            slideshow_imagens=True,
        )
        self.index_page.add_child(instance=aviso)
        aviso.save()

        self.assertTrue(aviso.slideshow_imagens)

    def test_get_imagem_destaque_com_imagem(self):
        """Testa get_imagem_destaque quando há imagens."""
        aviso = AvisosPage(
            title="Aviso Imagem",
            slug="aviso-imagem",
            descricao="Teste imagem",
        )
        self.index_page.add_child(instance=aviso)
        
        # Adicionar imagem via StreamField
        aviso.images = [
            ("imagem", self.test_image)
        ]
        aviso.save()

        imagem_destaque = aviso.get_imagem_destaque()
        self.assertIsNotNone(imagem_destaque)
        self.assertEqual(imagem_destaque.id, self.test_image.id)

    def test_get_imagem_destaque_sem_imagem(self):
        """Testa get_imagem_destaque quando não há imagens."""
        aviso = AvisosPage(
            title="Aviso Sem Imagem",
            slug="aviso-sem-imagem",
            descricao="Teste sem imagem",
        )
        self.index_page.add_child(instance=aviso)
        aviso.save()

        imagem_destaque = aviso.get_imagem_destaque()
        self.assertIsNone(imagem_destaque)

    def test_get_ultimos_avisos_destaques_primeiro(self):
        """Testa get_ultimos_avisos retorna destaques primeiro."""
        # Criar avisos: 3 destaques + 3 normais
        for i in range(3):
            aviso_destaque = AvisosPage(
                title=f"Destaque {i}",
                slug=f"destaque-{i}",
                descricao=f"Destaque {i}",
                destaque=True,
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=aviso_destaque)
            aviso_destaque.save_revision().publish()

        for i in range(3):
            aviso_normal = AvisosPage(
                title=f"Normal {i}",
                slug=f"normal-{i}",
                descricao=f"Normal {i}",
                destaque=False,
                data_publicacao=datetime(2025, 11, i + 10, 10, 0),
            )
            self.index_page.add_child(instance=aviso_normal)
            aviso_normal.save_revision().publish()

        primeiro_aviso = AvisosPage.objects.first()
        ultimos = primeiro_aviso.get_ultimos_avisos(quantidade=6)

        self.assertEqual(len(ultimos), 6)
        
        # Primeiros 3 devem ser destaques
        for i in range(3):
            self.assertTrue(ultimos[i].destaque, f"Posição {i} deveria ser destaque")

    def test_get_ultimos_avisos_limite_quantidade(self):
        """Testa get_ultimos_avisos respeita limite de quantidade."""
        # Criar 10 avisos
        for i in range(10):
            aviso = AvisosPage(
                title=f"Aviso {i}",
                slug=f"aviso-lim-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=aviso)
            aviso.save_revision().publish()

        primeiro_aviso = AvisosPage.objects.first()
        ultimos = primeiro_aviso.get_ultimos_avisos(quantidade=4)

        self.assertEqual(len(ultimos), 4)

    def test_get_context_inclui_ultimos_avisos(self):
        """Testa se get_context inclui ultimos_avisos."""
        aviso = AvisosPage(
            title="Aviso Context",
            slug="aviso-context",
            descricao="Teste de contexto",
        )
        self.index_page.add_child(instance=aviso)
        aviso.save_revision().publish()

        request = self.factory.get("/")
        context = aviso.get_context(request)

        self.assertIn("ultimos_avisos", context)

    def test_get_admin_display_title_com_destaque(self):
        """Testa get_admin_display_title adiciona ★ para avisos em destaque."""
        aviso_destaque = AvisosPage(
            title="Aviso Destaque",
            slug="aviso-dest-admin",
            descricao="Teste admin title",
            destaque=True,
        )
        self.index_page.add_child(instance=aviso_destaque)
        aviso_destaque.save()

        display_title = aviso_destaque.get_admin_display_title()
        self.assertTrue(display_title.startswith("★"))
        self.assertIn("Aviso Destaque", display_title)

    def test_get_admin_display_title_sem_destaque(self):
        """Testa get_admin_display_title sem ★ para avisos normais."""
        aviso_normal = AvisosPage(
            title="Aviso Normal",
            slug="aviso-norm-admin",
            descricao="Teste admin title",
            destaque=False,
        )
        self.index_page.add_child(instance=aviso_normal)
        aviso_normal.save()

        display_title = aviso_normal.get_admin_display_title()
        self.assertFalse(display_title.startswith("★"))
        self.assertEqual(display_title, "Aviso Normal")

    def test_parent_page_types(self):
        """Testa que AvisosPage só pode ser filho de AvisosIndexPage."""
        self.assertIn("AvisosIndexPage", AvisosPage.parent_page_types)
        self.assertEqual(len(AvisosPage.parent_page_types), 1)

    def test_subpage_types_vazio(self):
        """Testa que AvisosPage não permite subpáginas."""
        self.assertEqual(AvisosPage.subpage_types, [])


class AvisosIndexPageTestCase(TestCase):
    """Testes para o modelo AvisosIndexPage."""

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
            slug="home-idx-avisos-index",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Criar AvisosIndexPage
        cls.index_page = AvisosIndexPage(
            title="Avisos Index",
            slug="avisos-index-page",
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
        """Testa criação de AvisosIndexPage."""
        self.assertEqual(self.index_page.title, "Avisos Index")
        self.assertEqual(self.index_page.introduction, "Introdução de teste")
        self.assertTrue(self.index_page.live)

    def test_get_context_com_posts_paginados(self):
        """Testa get_context retorna posts paginados."""
        # Criar avisos
        for i in range(15):
            aviso = AvisosPage(
                title=f"Aviso {i}",
                slug=f"aviso-idx-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=aviso)
            aviso.save_revision().publish()

        request = self.factory.get("/avisos-index/")
        context = self.index_page.get_context(request)

        self.assertIn("posts", context)
        self.assertIsInstance(context["posts"], PaginatorPage)
        self.assertEqual(len(context["posts"]), 12)  # Padrão de 12 por página

    def test_get_context_paginacao_invalida_retorna_primeira_pagina(self):
        """Testa que página inválida retorna primeira página."""
        # Criar alguns avisos
        for i in range(5):
            aviso = AvisosPage(
                title=f"Aviso Pag {i}",
                slug=f"aviso-pag-inv-{i}",
                descricao=f"Descrição {i}",
            )
            self.index_page.add_child(instance=aviso)
            aviso.save_revision().publish()

        request = self.factory.get("/avisos-index/?page=abc")
        context = self.index_page.get_context(request)

        self.assertEqual(len(context["posts"]), 5)  # Todos na primeira página

    def test_get_posts_sem_tag(self):
        """Testa get_posts sem filtro de tag."""
        # Criar avisos
        for i in range(3):
            aviso = AvisosPage(
                title=f"Aviso GP {i}",
                slug=f"aviso-gp-{i}",
                descricao=f"Descrição {i}",
            )
            self.index_page.add_child(instance=aviso)
            aviso.save_revision().publish()

        posts = self.index_page.get_posts()
        self.assertEqual(posts.count(), 3)

    def test_get_posts_com_tag(self):
        """Testa get_posts filtrado por tag."""
        tag = Tag.objects.create(name="Urgente", slug="urgente")

        # Criar avisos com e sem tag
        aviso_com_tag = AvisosPage(
            title="Aviso Com Tag",
            slug="aviso-com-tag-gp",
            descricao="Com tag",
        )
        self.index_page.add_child(instance=aviso_com_tag)
        aviso_com_tag.save()
        aviso_com_tag.tags.add(tag)

        aviso_sem_tag = AvisosPage(
            title="Aviso Sem Tag",
            slug="aviso-sem-tag-gp",
            descricao="Sem tag",
        )
        self.index_page.add_child(instance=aviso_sem_tag)
        aviso_sem_tag.save()

        posts = self.index_page.get_posts(tag=tag)
        self.assertEqual(posts.count(), 1)
        self.assertEqual(posts.first().title, "Aviso Com Tag")

    def test_tag_archive_route_tag_existente(self):
        """Testa rota tag_archive com tag existente."""
        tag = Tag.objects.create(name="Comunicado", slug="comunicado")

        aviso = AvisosPage(
            title="Aviso Comunicado",
            slug="aviso-comunicado",
            descricao="Aviso com tag comunicado",
        )
        self.index_page.add_child(instance=aviso)
        aviso.save_revision().publish()
        aviso.tags.add(tag)

        request = self.factory.get(f"{self.index_page.url}tags/comunicado/")
        response = self.index_page.tag_archive(request, tag="comunicado")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Aviso Comunicado", response.content)

    def test_tag_archive_route_tag_inexistente(self):
        """Testa rota tag_archive com tag que não existe."""
        request = self.factory.get(f"{self.index_page.url}tags/inexistente/")
        response = self.index_page.tag_archive(request, tag="inexistente")

        # Deve redirecionar para a página index
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.index_page.url)

    def test_get_ultimos_avisos_index_destaques_primeiro(self):
        """Testa get_ultimos_avisos do índice retorna destaques primeiro."""
        # Criar 4 destaques
        for i in range(4):
            destaque = AvisosPage(
                title=f"Destaque Idx {i}",
                slug=f"dest-idx-{i}",
                descricao=f"Destaque {i}",
                destaque=True,
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=destaque)
            destaque.save_revision().publish()

        # Criar 4 normais
        for i in range(4):
            normal = AvisosPage(
                title=f"Normal Idx {i}",
                slug=f"norm-idx-{i}",
                descricao=f"Normal {i}",
                destaque=False,
                data_publicacao=datetime(2025, 11, i + 10, 10, 0),
            )
            self.index_page.add_child(instance=normal)
            normal.save_revision().publish()

        ultimos = self.index_page.get_ultimos_avisos(quantidade=6)

        self.assertEqual(len(ultimos), 6)
        # Primeiros 4 devem ser destaques
        for i in range(4):
            self.assertTrue(ultimos[i].destaque)

    def test_get_ultimos_avisos_completa_com_normais(self):
        """Testa que get_ultimos_avisos completa com normais se faltam destaques."""
        # Criar apenas 2 destaques
        for i in range(2):
            destaque = AvisosPage(
                title=f"Destaque {i}",
                slug=f"dest-comp-{i}",
                descricao=f"Destaque {i}",
                destaque=True,
                data_publicacao=datetime(2025, 11, i + 1, 10, 0),
            )
            self.index_page.add_child(instance=destaque)
            destaque.save_revision().publish()

        # Criar 5 normais
        for i in range(5):
            normal = AvisosPage(
                title=f"Normal Comp {i}",
                slug=f"norm-comp-{i}",
                descricao=f"Normal {i}",
                destaque=False,
                data_publicacao=datetime(2025, 11, i + 10, 10, 0),
            )
            self.index_page.add_child(instance=normal)
            normal.save_revision().publish()

        ultimos = self.index_page.get_ultimos_avisos(quantidade=6)

        self.assertEqual(len(ultimos), 6)
        # 2 destaques + 4 normais
        destaques_count = sum(1 for aviso in ultimos if aviso.destaque)
        self.assertEqual(destaques_count, 2)

    def test_parent_page_types_index(self):
        """Testa parent_page_types de AvisosIndexPage."""
        self.assertIn("home.HomePage", AvisosIndexPage.parent_page_types)
        self.assertIn("intranet.IntranetHomePage", AvisosIndexPage.parent_page_types)

    def test_subpage_types_index(self):
        """Testa que AvisosIndexPage só permite AvisosPage como filho."""
        self.assertEqual(AvisosIndexPage.subpage_types, ["AvisosPage"])


class IntegrationAvisosTestCase(TestCase):
    """Testes de integração para fluxo completo de avisos."""

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
            title="Home Integration Avisos",
            slug="home-integ-avisos-test",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Criar AvisosIndexPage
        cls.index_page = AvisosIndexPage(
            title="Avisos Integração",
            slug="avisos-integ-test",
            introduction="Teste de integração",
        )
        cls.home_page.add_child(instance=cls.index_page)
        cls.index_page.save_revision().publish()

    def setUp(self):
        """Setup por teste."""
        self.root_page.refresh_from_db()
        self.home_page.refresh_from_db()
        self.index_page.refresh_from_db()

    def test_fluxo_completo_criar_publicar_filtrar_aviso(self):
        """Teste de integração: criar → publicar → filtrar por tag."""
        # Criar aviso com tags e destaque
        tag = Tag.objects.create(name="Urgente", slug="urgente")

        aviso = AvisosPage(
            title="Aviso Urgente Importante",
            slug="aviso-urgente-importante",
            descricao="Descrição do aviso urgente",
            destaque=True,
            data_publicacao=datetime(2025, 11, 13, 14, 30),
        )
        self.index_page.add_child(instance=aviso)
        aviso.save_revision().publish()
        aviso.tags.add(tag)

        # Verificar publicação
        self.assertTrue(aviso.live)
        self.assertTrue(aviso.destaque)

        # Verificar display title no admin
        display_title = aviso.get_admin_display_title()
        self.assertTrue(display_title.startswith("★"))

        # Filtrar por tag
        posts_filtrados = self.index_page.get_posts(tag=tag)
        self.assertEqual(posts_filtrados.count(), 1)
        self.assertEqual(posts_filtrados.first().title, "Aviso Urgente Importante")

        # Verificar URL da tag
        tags_com_url = aviso.get_tags
        self.assertEqual(len(tags_com_url), 1)
        self.assertTrue(tags_com_url[0].url.endswith("tags/urgente/"))

    def test_fluxo_prioridade_destaques_em_listagem(self):
        """Testa fluxo onde destaques aparecem primeiro na listagem."""
        # Criar 3 avisos normais com datas recentes
        for i in range(3):
            normal = AvisosPage(
                title=f"Normal Recente {i}",
                slug=f"normal-rec-{i}",
                descricao=f"Normal {i}",
                destaque=False,
                data_publicacao=datetime(2025, 11, 13 - i, 10, 0),  # Datas recentes
            )
            self.index_page.add_child(instance=normal)
            normal.save_revision().publish()

        # Criar 2 destaques com datas antigas
        for i in range(2):
            destaque = AvisosPage(
                title=f"Destaque Antigo {i}",
                slug=f"dest-ant-{i}",
                descricao=f"Destaque {i}",
                destaque=True,
                data_publicacao=datetime(2025, 10, i + 1, 10, 0),  # Datas antigas
            )
            self.index_page.add_child(instance=destaque)
            destaque.save_revision().publish()

        # Buscar últimos avisos
        ultimos = self.index_page.get_ultimos_avisos(quantidade=5)

        # Destaques devem vir primeiro, mesmo sendo mais antigos
        self.assertEqual(len(ultimos), 5)
        self.assertTrue(ultimos[0].destaque)
        self.assertTrue(ultimos[1].destaque)
        self.assertFalse(ultimos[2].destaque)

    def test_fluxo_paginacao_multiplas_paginas(self):
        """Testa fluxo de paginação com múltiplas páginas."""
        # Criar 25 avisos
        for i in range(25):
            aviso = AvisosPage(
                title=f"Aviso Paginação {i}",
                slug=f"aviso-pag-flow-{i}",
                descricao=f"Descrição {i}",
                data_publicacao=datetime(2025, 11, 1, i % 24, i % 60),
            )
            self.index_page.add_child(instance=aviso)
            aviso.save_revision().publish()

        # Página 1
        request_p1 = self.factory.get("/avisos-integ/")
        context_p1 = self.index_page.get_context(request_p1)
        self.assertEqual(len(context_p1["posts"]), 12)

        # Página 2
        request_p2 = self.factory.get("/avisos-integ/?page=2")
        context_p2 = self.index_page.get_context(request_p2)
        self.assertEqual(len(context_p2["posts"]), 12)

        # Página 3 (restante)
        request_p3 = self.factory.get("/avisos-integ/?page=3")
        context_p3 = self.index_page.get_context(request_p3)
        self.assertEqual(len(context_p3["posts"]), 1)
