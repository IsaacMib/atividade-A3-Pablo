from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page

from home.models import HomePage
from intranet.models import IntranetHomePage
from dicas_presidente.models import DicasPresidenteIndexPage, DicasPresidentePage


class DicasPresidentePageTestCase(WagtailPageTestCase):
    """Test suite for DicasPresidentePage functionality"""

    def setUp(self):
        """Set up test data"""
        # Get the root page
        root = Page.objects.get(id=1)

        # Create HomePage
        self.home = HomePage(title="Home Test", slug="home-test-dicas")
        root.add_child(instance=self.home)

        # Create IntranetHomePage
        self.intranet = IntranetHomePage(title="Intranet Test", slug="intranet-test-dicas")
        self.home.add_child(instance=self.intranet)

        # Create DicasPresidenteIndexPage
        self.index_page = DicasPresidenteIndexPage(
            title="Dicas do Presidente", slug="dicas-presidente-test"
        )
        self.intranet.add_child(instance=self.index_page)

    def test_create_dicas_page_with_slideshow(self):
        """Test creating a DicasPresidentePage with slideshow enabled"""
        dica = DicasPresidentePage(
            title="Dica com Slideshow",
            slug="dica-slideshow",
            descricao="Teste de dica com slideshow ativado",
            slideshow_imagens=True,
        )
        self.index_page.add_child(instance=dica)

        self.assertTrue(dica.slideshow_imagens)
        self.assertEqual(dica.get_parent(), self.index_page)

    def test_create_dicas_page_single_image(self):
        """Test creating a DicasPresidentePage with single image (no slideshow)"""
        dica = DicasPresidentePage(
            title="Dica Imagem Única",
            slug="dica-single",
            descricao="Teste de dica com imagem única",
            slideshow_imagens=False,
        )
        self.index_page.add_child(instance=dica)

        self.assertFalse(dica.slideshow_imagens)

    def test_dicas_page_renders_successfully(self):
        """Test that DicasPresidentePage renders without errors"""
        dica = DicasPresidentePage(
            title="Dica de Teste",
            slug="dica-teste",
            descricao="Teste de renderização de dica",
        )
        self.index_page.add_child(instance=dica)

        response = self.client.get(dica.url)
        self.assertEqual(response.status_code, 200)

    def test_slideshow_imagens_defaults_to_false(self):
        """Test that slideshow_imagens field defaults to False"""
        dica = DicasPresidentePage(
            title="Dica Default",
            slug="dica-default",
            descricao="Teste do valor padrão de slideshow",
        )
        self.index_page.add_child(instance=dica)

        # Should default to False
        self.assertFalse(dica.slideshow_imagens)

    def test_dicas_page_has_imagens_dica_field(self):
        """Test that DicasPresidentePage has imagens_dica StreamField"""
        dica = DicasPresidentePage(
            title="Dica Teste Campos",
            slug="dica-campos",
            descricao="Teste de campos da dica",
        )
        self.index_page.add_child(instance=dica)

        # Check field exists
        self.assertTrue(hasattr(dica, "imagens_dica"))

    def test_index_page_can_have_multiple_dicas(self):
        """Test that DicasPresidenteIndexPage can have multiple child pages"""
        dica1 = DicasPresidentePage(
            title="Dica 1",
            slug="dica-1",
            descricao="Primeira dica de teste",
        )
        dica2 = DicasPresidentePage(
            title="Dica 2",
            slug="dica-2",
            descricao="Segunda dica de teste",
        )

        self.index_page.add_child(instance=dica1)
        self.index_page.add_child(instance=dica2)

        children = self.index_page.get_children().live()
        self.assertEqual(children.count(), 2)

    def test_destaque_flag_defaults_to_false(self):
        """Test that destaque field defaults to False"""
        dica = DicasPresidentePage(
            title="Dica Destaque Test",
            slug="dica-destaque",
            descricao="Teste do campo destaque",
        )
        self.index_page.add_child(instance=dica)

        self.assertFalse(dica.destaque)
