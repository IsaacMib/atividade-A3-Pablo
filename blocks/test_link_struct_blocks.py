from django.test import TestCase
from django.core.exceptions import ValidationError

from wagtail.models import Site, Collection
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from core.utils_test import ensure_root_page
from home.models import HomePage
from blocks.models import (
    LinkStructBlock,
    LinkWithImageStructBlock,
    CardLinhaDoTempoBlock,
)


class LinkStructBlockTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Root compartilhada e limpa
        cls.root_page = ensure_root_page()
        for child in cls.root_page.get_children():
            child.delete()
        cls.root_page.refresh_from_db()

        # Site padrão para que .url funcione
        if not Site.objects.filter(is_default_site=True).exists():
            Site.objects.create(
                hostname='localhost',
                port=80,
                root_page=cls.root_page,
                is_default_site=True,
                site_name='Test Site',
            )

        # Página interna para testes
        cls.home_page = HomePage(title='Home', slug='home')
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.refresh_from_db()

        cls.block = LinkStructBlock()

    def test_clean_empty_raises(self):
        with self.assertRaises(ValidationError):
            self.block.clean({'link_text': 'Texto', 'internal_page': None, 'external_url': ''})

    def test_clean_both_filled_raises(self):
        with self.assertRaises(ValidationError):
            self.block.clean({
                'link_text': 'Texto',
                'internal_page': self.home_page,
                'external_url': 'https://example.com',
            })

    def test_clean_internal_ok(self):
        cleaned = self.block.clean({
            'link_text': 'Texto',
            'internal_page': self.home_page,
            'external_url': None,
        })
        self.assertEqual(getattr(cleaned['internal_page'], 'id', None), self.home_page.id)
        self.assertFalse(bool(cleaned.get('external_url')))

    def test_clean_external_ok(self):
        cleaned = self.block.clean({
            'link_text': 'Texto',
            'internal_page': None,
            'external_url': 'https://example.org',
        })
        self.assertEqual(cleaned['external_url'], 'https://example.org')
        self.assertIsNone(cleaned.get('internal_page'))

    def test_get_url_internal(self):
        value = {
            'link_text': 'Texto',
            'internal_page': self.home_page,
            'external_url': None,
        }
        # Usa método da própria block para obter url
        url = self.block.get_url(value)
        self.assertEqual(url, self.home_page.url)

    def test_get_url_external(self):
        link = 'https://example.org/path'
        value = {
            'link_text': 'Texto',
            'internal_page': None,
            'external_url': link,
        }
        url = self.block.get_url(value)
        self.assertEqual(url, link)


class LinkWithImageStructBlockTestCase(TestCase):
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

        cls.home_page = HomePage(title='Home', slug='home')
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.refresh_from_db()

        # Garantir Collection root para criar imagens, se necessário
        if not Collection.objects.filter(depth=1).exists():
            Collection.add_root(name='Root')

        cls.img = Image.objects.create(title='Img', file=get_test_image_file())

        cls.block = LinkWithImageStructBlock()

    def test_get_url_nested_internal(self):
        # to_python converte IDs em objetos, então vamos usar o valor já processado
        value = {
            'link_text': '<p>Link</p>',
            'link': {
                'link_text': 'Link',
                'internal_page': self.home_page.id,
                'external_url': None,
            },
            'image': self.img.id,
        }
        # Processar value primeiro via to_python
        processed = self.block.to_python(value)
        url = self.block.get_url(processed)
        self.assertEqual(url, self.home_page.url)

    def test_get_url_nested_external(self):
        external = 'https://pb.gov.br/'
        value = {
            'link_text': '<p>Link</p>',
            'link': {
                'link_text': 'Link',
                'internal_page': None,
                'external_url': external,
            },
            'image': self.img.id,
        }
        processed = self.block.to_python(value)
        url = self.block.get_url(processed)
        self.assertEqual(url, external)

    def test_get_url_legacy_fields_fallback(self):
        # Compat com conteúdo salvo antes da migração
        # Simular dados legados (sem 'link', com campos antigos no dicionário)
        external = 'https://legacy.example/'
        value = {
            'link_text': '<p>Link</p>',
            # Sem campo 'link'; usa fallback nos campos antigos
            'internal_page': None,
            'external_url': external,
            'image': self.img.id,
        }
        # Passar dict direto para simular dados legados (sem to_python que espera novos campos)
        url = self.block.get_url(value)
        self.assertEqual(url, external)


class CardLinhaDoTempoBlockTestCase(TestCase):
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

        cls.home_page = HomePage(title='Home', slug='home')
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.refresh_from_db()

        if not Collection.objects.filter(depth=1).exists():
            Collection.add_root(name='Root')
        cls.img = Image.objects.create(title='Img', file=get_test_image_file())

        cls.block = CardLinhaDoTempoBlock()

    def _base_value(self):
        return {
            'imagem': self.img.id,  # Passar ID, não instância
            'texto_alternativo': 'alt',
            'titulo': 'Titulo',
            'descricao_linha_do_tempo': 'desc',
            'adicionarLink': False,
        }

    def test_clean_requires_link_when_toggle_on(self):
        value = self._base_value()
        value['adicionarLink'] = True
        # link vazio/None, mas validação vem do StructBlock filho
        # Simplesmente omitir ou passar estrutura vazia
        with self.assertRaises(ValidationError):
            self.block.clean(value)

    def test_clean_allows_no_link_when_toggle_off(self):
        value = self._base_value()
        cleaned = self.block.clean(value)
        self.assertFalse(cleaned.get('adicionarLink'))
        self.assertIsNone(cleaned.get('link'))

    def test_value_get_url_internal(self):
        value = self._base_value()
        value['adicionarLink'] = True
        value['link'] = {
            'link_text': 'Link',
            'internal_page': self.home_page.id,  # ID
            'external_url': None,
        }
        # to_python retorna StructValue com métodos utilitários
        struct_value = self.block.to_python(value)
        self.assertTrue(hasattr(struct_value, 'get_url'))
        self.assertEqual(struct_value.get_url(), self.home_page.url)

    def test_value_get_url_external(self):
        external = 'https://example.com/x'
        value = self._base_value()
        value['adicionarLink'] = True
        value['link'] = {
            'link_text': 'Link',
            'internal_page': None,
            'external_url': external,
        }
        struct_value = self.block.to_python(value)
        self.assertEqual(struct_value.get_url(), external)

    def test_value_get_url_legacy_fallback(self):
        # Compatibilidade com conteúdo antigo, sem campo "link"
        # Simular dados legados: omitir 'link', usar campos diretos antigos
        external = 'https://legacy.example/x'
        # Criar valor legado SEM campo 'link' para simular dados antigos
        # Como CardLinhaDoTempoBlock agora tem campo 'link', to_python vai tentar processá-lo
        # Então, validar via StructValue direto (passando dict que simula dados salvos)
        from blocks.models import CardLinhaDoTempoValue
        legacy_data = {
            'imagem': self.img.id,
            'texto_alternativo': 'alt',
            'titulo': 'Titulo',
            'descricao_linha_do_tempo': 'desc',
            'adicionarLink': True,
            # Sem 'link' (campo novo)
            'internal_page': None,
            'external_url': external,
        }
        # Criar StructValue direto com dados legados
        struct_value = CardLinhaDoTempoValue(self.block, legacy_data)
        self.assertEqual(struct_value.get_url(), external)

    def test_form_attrs_targets_point_to_nested_fields(self):
        # Garante que o widget do admin aponte para os campos aninhados corretos
        targets = self.block.meta.form_attrs.get('data-card-links-target-fields-value')
        self.assertEqual(targets, 'link-internal_page,link-external_url')
