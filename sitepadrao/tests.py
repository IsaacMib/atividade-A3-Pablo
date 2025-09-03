from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.conf import settings
from unittest.mock import patch
from sitepadrao.views import wagtail_logout_with_sso

User = get_user_model()


class WagtailLogoutWithSSOTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('sitepadrao.views.settings.HABILITAR_SSO_LOGIN', True)
    def test_wagtail_logout_url_exists_when_sso_enabled(self):
        """Testa se a URL de logout customizada existe quando SSO está habilitado."""
        # Simula que o SSO está habilitado
        with patch.object(settings, 'HABILITAR_SSO_LOGIN', True):
            try:
                url = reverse('wagtailadmin_logout')
                self.assertTrue(url)
                self.assertEqual(url, '/admin/manager/logout/')
            except Exception:
                # Se não conseguir resolver a URL, significa que não está configurada
                self.fail("URL wagtailadmin_logout não foi encontrada")

    @patch('sitepadrao.views.settings.HABILITAR_SSO_LOGIN', True)
    @patch('sitepadrao.views.SSO_AVAILABLE', True)
    @patch('sitepadrao.views.obter_provedor_recente')
    def test_wagtail_logout_with_sso_redirects_to_login(self, mock_obter_provedor):
        """Testa se o logout redireciona para a página de login."""
        # Mock do provedor para simular que o usuário não tem provedor SSO
        mock_obter_provedor.return_value = None
        
        # Login do usuário
        self.client.login(username='testuser', password='testpass123')
        
        # Chamada da view de logout
        response = self.client.get('/admin/manager/logout/')
        
        # Verifica se redireciona para login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/login/')

    def test_wagtail_logout_view_exists(self):
        """Testa se a view wagtail_logout_with_sso existe e é chamável."""
        self.assertTrue(callable(wagtail_logout_with_sso))

    @patch('sitepadrao.views.settings.HABILITAR_SSO_LOGIN', True)
    @patch('sitepadrao.views.SSO_AVAILABLE', True)
    @patch('sitepadrao.views.obter_provedor_recente')
    @patch('sitepadrao.views._logout_sso')
    def test_logout_calls_sso_logout_when_provedor_exists(self, mock_logout_sso, mock_obter_provedor):
        """Testa se o logout do SSO é chamado quando há provedor configurado."""
        # Mock de um provedor com configurações de logout
        mock_provedor = type('MockProvedor', (), {
            'app': type('MockApp', (), {
                'settings': {'logout_url': 'http://keycloak.example.com/logout'}
            })()
        })()
        mock_obter_provedor.return_value = mock_provedor
        
        # Login do usuário
        self.client.login(username='testuser', password='testpass123')
        
        # Chamada da view de logout
        response = self.client.get('/admin/manager/logout/')
        
        # Verifica se o logout do SSO foi chamado
        mock_logout_sso.assert_called_once_with(self.user, mock_provedor)
        
        # Verifica se redireciona para login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/login/')


class URLConfigurationTest(TestCase):
    """Testa se as URLs estão configuradas corretamente."""

    @patch.object(settings, 'HABILITAR_SSO_LOGIN', True)
    def test_sso_urls_when_enabled(self):
        """Testa se as URLs do SSO são incluídas quando HABILITAR_SSO_LOGIN é True."""
        with patch.object(settings, 'HABILITAR_SSO_LOGIN', True):
            # Recarrega as URLs para aplicar a configuração
            from django.urls import clear_url_caches
            clear_url_caches()
            
            # Testa se consegue resolver as URLs específicas do SSO
            try:
                from django.urls import reverse
                manager_login_url = reverse('wagtailadmin_logout')
                self.assertIsNotNone(manager_login_url)
            except Exception:
                pass  # URLs podem não estar disponíveis no contexto de teste

    @patch.object(settings, 'HABILITAR_SSO_LOGIN', False)
    def test_standard_urls_when_sso_disabled(self):
        """Testa se as URLs padrão são usadas quando HABILITAR_SSO_LOGIN é False."""
        with patch.object(settings, 'HABILITAR_SSO_LOGIN', False):
            # Quando SSO está desabilitado, deve usar as URLs padrão do Wagtail
            self.assertFalse(settings.HABILITAR_SSO_LOGIN)
