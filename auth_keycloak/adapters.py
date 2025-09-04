import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from .utils import obter_provedor_recente, logout_sso, pode_fazer_logout_sso

LOGGER = logging.getLogger(__name__)
UserModel = get_user_model()

class KeycloakAdapter(DefaultAccountAdapter):
    """Adaptador do allauth para lidar com logout do acesso restrito.

    Funciona fazendo uma tentativa de post para o endpoint de encerrar
    sessão do keycloak antes de prosseguir com o logout do UserModel do
    Django.
    """

    def get_logout_redirect_url(self, request):
        """Gancho para processar logout junto ao SSO."""
        user = request.user
        provedor = obter_provedor_recente(user)
        
        # Quando não há provedor associado é porque o usuário é local. Faz o redirect padrão.
        if pode_fazer_logout_sso(user, provedor):
            if user.is_authenticated:
                logout_sso(user, provedor)
            else:
                raise ImmediateHttpResponse(redirect("informacoes:landing-page"))
        
        return super().get_logout_redirect_url(request)