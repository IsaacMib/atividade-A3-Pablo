from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.test import TransactionTestCase
from unittest.mock import patch, MagicMock

from taggit.models import Tag

try:
    from noticias.models import NoticiasPage, NoticiasIndexPages
    from home.models import HomePage
    NOTICIAS_AVAILABLE = True
except ImportError:
    NOTICIAS_AVAILABLE = False


class APIUrlsTestCase(APITestCase):
    """
    Testa todas as rotas definidas em api/urls.py
    """

    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário e grupo de integração
        self.integration_group, _ = Group.objects.get_or_create(name='Usuário de integração')
        self.integration_user = User.objects.create_user(
            username='integration_user',
            email='integration@test.com',
            password='testpass123'
        )
        self.integration_user.groups.add(self.integration_group)
        
        # Criar usuário comum (sem permissão)
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@test.com', 
            password='testpass123'
        )
        
        # Criar tokens
        self.integration_token = Token.objects.create(user=self.integration_user)
        self.regular_token = Token.objects.create(user=self.regular_user)
        
        # Configurar cliente API
        self.client = APIClient()

    def test_get_token_url_exists(self):
        """Testa se a URL de obtenção de token existe e responde corretamente"""
        url = reverse('api:get_token')
        
        # Teste com credenciais válidas
        response = self.client.post(url, {
            'username': 'integration_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        # Teste com credenciais inválidas
        response = self.client.post(url, {
            'username': 'invalid_user',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_url_methods(self):
        """Testa métodos HTTP permitidos na URL de token"""
        url = reverse('api:get_token')
        
        # POST deve funcionar
        response = self.client.post(url, {
            'username': 'integration_user', 
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # GET não deve funcionar
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_shared_content_by_tag_url_authentication(self):
        """Testa autenticação na URL de conteúdo por tag"""
        url = reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'test-tag'})
        
        # Sem autenticação
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Com usuário sem permissão
        self.client.force_authenticate(user=self.regular_user, token=self.regular_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Com usuário de integração
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        response = self.client.get(url)
        # Deve retornar 404 para tag inexistente, mas autorização OK
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_shared_content_by_tag_url_with_existing_tag(self):
        """Testa URL de conteúdo por tag com tag existente"""
        # Criar uma tag
        tag = Tag.objects.create(name='Test Tag', slug='test-tag')
        
        url = reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'test-tag'})
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        with override_settings(API_CONTEUDO_AGRUPADO=True):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)

    def test_all_shared_content_url_authentication(self):
        """Testa autenticação na URL de todo conteúdo compartilhado"""
        url = reverse('api:all_shared_content')
        
        # Sem autenticação
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Com usuário sem permissão
        self.client.force_authenticate(user=self.regular_user, token=self.regular_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Com usuário de integração
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_shared_content_url_response_format(self):
        """Testa formato de resposta da URL de todo conteúdo"""
        url = reverse('api:all_shared_content')
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_single_noticia_url_authentication(self):
        """Testa autenticação na URL de notícia única"""
        url = reverse('api:single_noticia_content', kwargs={'pk': 1})
        
        # Sem autenticação
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Com usuário sem permissão
        self.client.force_authenticate(user=self.regular_user, token=self.regular_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Com usuário de integração
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        response = self.client.get(url)
        # Deve retornar 404 para notícia inexistente, mas autorização OK
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_url_patterns_coverage(self):
        """Testa se todas as URLs definidas em urls.py são acessíveis"""
        # URLs que devem existir baseadas no arquivo urls.py
        expected_urls = [
            'api:get_token',
            'api:shared_content_by_tag',
            'api:all_shared_content', 
            'api:single_noticia_content',
        ]
        
        for url_name in expected_urls:
            if url_name == 'api:shared_content_by_tag':
                url = reverse(url_name, kwargs={'tag_slug': 'test'})
            elif url_name == 'api:single_noticia_content':
                url = reverse(url_name, kwargs={'pk': 1})
            else:
                url = reverse(url_name)
            
            # Verificar se a URL existe (não testa funcionalidade, apenas existência)
            self.assertIsNotNone(url)

    def test_api_url_query_parameters(self):
        """Testa URLs com parâmetros de query"""
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        # Teste com parâmetros de query na URL all_shared_content
        url = reverse('api:all_shared_content')
        response = self.client.get(url, {'noticias': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Teste com tag e parâmetros
        tag = Tag.objects.create(name='Test Tag', slug='query-test')
        url = reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'query-test'})
        response = self.client.get(url, {'noticias': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(API_CONTEUDO_AGRUPADO=True)
    def test_api_grouped_content_setting(self):
        """Testa comportamento com configuração de conteúdo agrupado ativa"""
        tag = Tag.objects.create(name='Grouped Test', slug='grouped-test')
        url = reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'grouped-test'})
        
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Com agrupamento ativo, resposta deve ser um dict
        self.assertIsInstance(response.data, dict)

    @override_settings(API_CONTEUDO_AGRUPADO=False)
    def test_api_ungrouped_content_setting(self):
        """Testa comportamento com configuração de conteúdo agrupado inativa"""
        tag = Tag.objects.create(name='Ungrouped Test', slug='ungrouped-test')
        url = reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'ungrouped-test'})
        
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Sem agrupamento, resposta deve ser uma lista
        self.assertIsInstance(response.data, list)

    def test_api_invalid_tag_slug(self):
        """Testa comportamento com slug de tag inválido"""
        url = reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'nonexistent-tag'})
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_api_invalid_noticia_pk(self):
        """Testa comportamento com PK de notícia inválido"""
        url = reverse('api:single_noticia_content', kwargs={'pk': 99999})
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_api_cors_headers(self):
        """Testa se as respostas da API têm headers apropriados"""
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        url = reverse('api:all_shared_content')
        response = self.client.get(url)
        
        # Verificar tipo de conteúdo JSON
        self.assertEqual(response['Content-Type'], 'application/json')

    def tearDown(self):
        """Limpeza após cada teste"""
        self.client.logout()


@override_settings(DEBUG=True)
class APIPerformanceTestCase(APITestCase):
    """
    Testes de performance básicos para as rotas da API
    """

    def setUp(self):
        self.integration_group, _ = Group.objects.get_or_create(name='Usuário de integração')
        self.integration_user = User.objects.create_user(
            username='perf_user',
            email='perf@test.com',
            password='testpass123'
        )
        self.integration_user.groups.add(self.integration_group)
        self.integration_token = Token.objects.create(user=self.integration_user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)

    def test_api_response_times(self):
        """Testa se as APIs respondem em tempo hábil"""
        import time
        
        urls_to_test = [
            reverse('api:all_shared_content'),
        ]
        
        for url in urls_to_test:
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # API deve responder em menos de 2 segundos
            self.assertLess(response_time, 2.0, 
                           f"API {url} demorou {response_time:.2f}s para responder")
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIErrorHandlingTestCase(APITestCase):
    """
    Testes de tratamento de erros da API
    """

    def setUp(self):
        self.integration_group, _ = Group.objects.get_or_create(name='Usuário de integração')
        self.integration_user = User.objects.create_user(
            username='error_user',
            email='error@test.com',
            password='testpass123'
        )
        self.integration_user.groups.add(self.integration_group)
        self.integration_token = Token.objects.create(user=self.integration_user)
        self.client = APIClient()

    def test_invalid_token_authentication(self):
        """Testa autenticação com token inválido"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token_here')
        
        url = reverse('api:all_shared_content')
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_malformed_request_data(self):
        """Testa requisições com dados malformados"""
        url = reverse('api:get_token')
        
        # Dados incompletos
        response = self.client.post(url, {'username': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Dados vazios
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_http_methods_not_allowed(self):
        """Testa métodos HTTP não permitidos"""
        urls_get_only = [
            reverse('api:all_shared_content'),
            reverse('api:shared_content_by_tag', kwargs={'tag_slug': 'test'}),
            reverse('api:single_noticia_content', kwargs={'pk': 1}),
        ]
        
        self.client.force_authenticate(user=self.integration_user, token=self.integration_token)
        
        for url in urls_get_only:
            # POST não deve ser permitido nessas URLs
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            
            # PUT não deve ser permitido
            response = self.client.put(url, {})
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            
            # DELETE não deve ser permitido
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


if NOTICIAS_AVAILABLE:
    class APIWithNoticiasTestCase(TransactionTestCase):
        """
        Testes específicos para quando o modelo NoticiasPage está disponível
        """

        def setUp(self):
            self.integration_group, _ = Group.objects.get_or_create(name='Usuário de integração')
            self.integration_user = User.objects.create_user(
                username='noticias_user',
                email='noticias@test.com',
                password='testpass123'
            )
            self.integration_user.groups.add(self.integration_group)
            self.integration_token = Token.objects.create(user=self.integration_user)
            self.client = APIClient()
            self.client.force_authenticate(user=self.integration_user, token=self.integration_token)

        @patch('api.views.NoticiasPage')
        def test_api_with_mock_noticias(self, mock_noticias):
            """Testa APIs com mock do modelo NoticiasPage"""
            # Configurar mock
            mock_instance = MagicMock()
            mock_instance.id = 1
            mock_instance.title = 'Test Noticia'
            mock_instance.url = '/test-noticia/'
            mock_noticias.objects.live.return_value.public.return_value.order_by.return_value = [mock_instance]
            
            url = reverse('api:all_shared_content')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, list)

        def test_single_noticia_invalid_id_type(self):
            """Testa single_noticia com tipo de ID inválido"""
            # URL com string em vez de int para pk causará erro na resolução da URL
            with self.assertRaises(Exception):
                reverse('api:single_noticia_content', kwargs={'pk': 'invalid'})
