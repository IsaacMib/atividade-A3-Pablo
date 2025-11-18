from django.test import TestCase
from django.core.exceptions import ValidationError
from wagtail.models import Site

from core.utils_test import ensure_root_page
from home.models import HomePage
from blocks.models import LinkBlock, AcessosRapidosBlock


class LinkBlockTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Root page compartilhada entre testes; limpar filhos para evitar conflitos
        cls.root_page = ensure_root_page()
        for child in cls.root_page.get_children():
            child.delete()
        cls.root_page.refresh_from_db()

        # Criar Site padrão para que Page.url funcione
        if not Site.objects.filter(is_default_site=True).exists():
            Site.objects.create(
                hostname='localhost',
                port=80,
                root_page=cls.root_page,
                is_default_site=True,
                site_name='Test Site',
            )

        # Criar HomePage publicada para usar como internal_page
        cls.home_page = HomePage(
            title="Home Test",
            slug="home-test",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.refresh_from_db()

        cls.block = LinkBlock()

    def test_clean_both_empty_raises(self):
        with self.assertRaises(ValidationError):
            self.block.clean({
                'internal_page': None,
                'external_url': '',
            })

    def test_clean_both_filled_raises(self):
        with self.assertRaises(ValidationError):
            self.block.clean({
                'internal_page': self.home_page,
                'external_url': 'https://example.com',
            })

    def test_clean_internal_only_ok(self):
        cleaned = self.block.clean({
            'internal_page': self.home_page.id,
            'external_url': None,
            'target': '_self',
        })
        # PageChooserBlock.clean() retorna instância de Page; comparar pelo id
        self.assertEqual(getattr(cleaned['internal_page'], 'id', None), self.home_page.id)
        # URLBlock pode normalizar None para string vazia
        self.assertFalse(bool(cleaned.get('external_url')))

    def test_clean_external_only_ok(self):
        cleaned = self.block.clean({
            'internal_page': None,
            'external_url': 'https://example.com',
            'target': '_blank',
        })
        self.assertEqual(cleaned['external_url'], 'https://example.com')
        self.assertIsNone(cleaned.get('internal_page'))

    def test_structvalue_url_internal(self):
        value = self.block.to_python({
            'internal_page': self.home_page.id,
            'external_url': None,
        })
        # Deve resolver para a URL da página publicada
        self.assertIsNotNone(value.url())
        self.assertEqual(value.url(), self.home_page.url)

    def test_structvalue_url_external(self):
        url = 'https://example.org/path'
        value = self.block.to_python({
            'internal_page': None,
            'external_url': url,
        })
        self.assertEqual(value.url(), url)


class AcessosRapidosRenderTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        for child in cls.root_page.get_children():
            child.delete()
        cls.root_page.refresh_from_db()

        if not Site.objects.filter(is_default_site=True).exists():
            Site.objects.create(
                hostname='localhost',
                port=80,
                root_page=cls.root_page,
                is_default_site=True,
                site_name='Test Site',
            )

        cls.home_page = HomePage(
            title="Home Test",
            slug="home-test",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.refresh_from_db()

        cls.block = AcessosRapidosBlock()

    def test_render_internal_link_includes_href(self):
        value = {
            'titulo': 'Acessos Rápidos',
            'itens': [
                {
                    'titulo': 'Item Interno',
                    'link': {
                        'internal_page': self.home_page.id,
                        'external_url': None,
                        'target': '_self',
                    },
                    'icone': 'fas fa-globe',
                }
            ],
        }
        html = self.block.render(self.block.to_python(value))
        self.assertIn('href="{}"'.format(self.home_page.url), html)
        # target="_self" pode ou não estar presente (é padrão do browser)

    def test_render_external_link_includes_href(self):
        external = 'https://portal.pb.gov.br/'
        value = {
            'titulo': 'Acessos Rápidos',
            'itens': [
                {
                    'titulo': 'Item Externo',
                    'link': {
                        'internal_page': None,
                        'external_url': external,
                        'target': '_blank',
                    },
                    'icone': 'fas fa-globe',
                }
            ],
        }
        html = self.block.render(self.block.to_python(value))
        self.assertIn('href="{}"'.format(external), html)
        self.assertIn('target="_blank"', html)

    def test_render_legacy_string_link_includes_href(self):
        # Compatibilidade com conteúdo antigo: link como string simples
        legacy_url = 'https://antigo.example.com/path'
        value = {
            'titulo': 'Acessos Rápidos',
            'itens': [
                {
                    'titulo': 'Item Antigo',
                    'link': legacy_url,  # antes era URLBlock
                    'icone': 'fas fa-globe',
                }
            ],
        }
        # Simular conteúdo legado sem conversão explícita
        html = self.block.render(value)
        self.assertIn('href=\"{}\"'.format(legacy_url), html)
