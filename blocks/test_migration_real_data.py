"""
Teste REAL de migração - Cria página com formato ANTIGO e valida transformação.
"""
from django.test import TestCase
from wagtail.models import Site, Collection
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from core.utils_test import ensure_root_page
from home.models import HomePage
import json


class MigrationRealDataTestCase(TestCase):
    """Teste que cria página REAL com formato antigo."""
    
    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        for child in cls.root_page.get_children():
            child.delete()
        cls.root_page.refresh_from_db()
        
        if not Site.objects.filter(is_default_site=True).exists():
            Site.objects.create(
                hostname='localhost', port=80,
                root_page=cls.root_page,
                is_default_site=True,
                site_name='Test Site',
            )
        
        if not Collection.objects.filter(depth=1).exists():
            Collection.add_root(name="Root")
        
        cls.test_image = Image.objects.create(
            title="Test Image",
            file=get_test_image_file(),
        )
        
        cls.home_ref = HomePage(
            title="Home Ref",
            slug="home-ref-mig",
        )
        cls.root_page.add_child(instance=cls.home_ref)
        cls.home_ref.save_revision().publish()
    
    def setUp(self):
        self.root_page.refresh_from_db()
        self.home_ref.refresh_from_db()
    
    def test_old_format_created_and_migrated(self):
        """✅ Cria página com formato ANTIGO e valida transformação."""
        # Criar página
        page = HomePage(title="Test Old", slug="test-old-mig")
        self.root_page.add_child(instance=page)
        
        # Dados ANTIGOS - campos diretos internal_page/external_url
        old_data = [{
            'type': 'linha_do_tempo',
            'value': {
                'titulo': 'História',
                'cards': [
                    {'type': 'card', 'value': {
                        'imagem': self.test_image.id,
                        'titulo': 'Evento 1',
                        'descricao_linha_do_tempo': 'Desc 1',
                        'adicionarLink': True,
                        'internal_page': self.home_ref.id,  # ANTIGO
                        'external_url': None,
                    }},
                    {'type': 'card', 'value': {
                        'imagem': self.test_image.id,
                        'titulo': 'Evento 2',
                        'descricao_linha_do_tempo': 'Desc 2',
                        'adicionarLink': True,
                        'internal_page': None,
                        'external_url': 'https://example.com',  # ANTIGO
                    }},
                ],
            },
        }]
        
        # Salvar diretamente
        HomePage.objects.filter(id=page.id).update(body=json.dumps(old_data))
        page.refresh_from_db()
        
        # VALIDAR: Formato ANTIGO
        data = page.body.raw_data  # Retorna lista Python
        card1 = data[0]['value']['cards'][0]['value']
        card2 = data[0]['value']['cards'][1]['value']
        
        print("\n🔍 FORMATO ANTIGO criado:")
        print(f"   Card 1 - internal_page: {card1.get('internal_page')}")
        print(f"   Card 1 - link: {card1.get('link', 'NÃO EXISTE ✓')}")
        
        self.assertIn('internal_page', card1)
        self.assertNotIn('link', card1, "link NÃO deve existir no formato antigo")
        self.assertIn('external_url', card2)
        self.assertNotIn('link', card2)
        
        # MIGRAR com lógica da migration 0007
        def transform(block):
            if 'link' in block:
                return block, False
            if 'internal_page' in block or 'external_url' in block:
                block['link'] = {
                    'internal_page': block.pop('internal_page', None),
                    'external_url': block.pop('external_url', None),
                    'link_text': '',
                }
                return block, True
            return block, False
        
        count = 0
        for item in data:
            if item.get('type') == 'linha_do_tempo':
                for card in item.get('value', {}).get('cards', []):
                    if card.get('type') == 'card':
                        card['value'], migrated = transform(card['value'])
                        if migrated:
                            count += 1
        
        # VALIDAR: Formato NOVO
        card1_new = data[0]['value']['cards'][0]['value']
        card2_new = data[0]['value']['cards'][1]['value']
        
        print(f"\n✨ MIGRAÇÃO aplicada ({count} cards):")
        print(f"   Card 1 - link: {card1_new.get('link')}")
        
        self.assertEqual(count, 2)
        self.assertNotIn('internal_page', card1_new)
        self.assertIn('link', card1_new)
        self.assertEqual(card1_new['link']['internal_page'], self.home_ref.id)
        self.assertIsNone(card1_new['link']['external_url'])
        
        self.assertNotIn('external_url', card2_new)
        self.assertIn('link', card2_new)
        self.assertIsNone(card2_new['link']['internal_page'])
        self.assertEqual(card2_new['link']['external_url'], 'https://example.com')
        
        print("✅ Teste completo: Formato antigo → Migração → Formato novo")
