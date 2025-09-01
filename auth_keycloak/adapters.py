import logging


import requests
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect

from django.contrib.auth import get_user_model
from .utils import obter_provedor_recente

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
        self.provedor = obter_provedor_recente(user)
        """ Quando não há provedor associado é porque o usuário é local. Faz o redirect padrão. """
        if (
            self.provedor
            and self.provedor.app
            and "logout_url" in self.provedor.app.settings
            and self.provedor.app.settings["logout_url"] != ""
        ):
            if user.is_authenticated:
                self._logout(user)
            else:
                raise ImmediateHttpResponse(redirect("informacoes:landing-page"))
        return super().get_logout_redirect_url(request)

    def _logout(self, user: UserModel) -> None:
        """Faz logout do SSO."""
        try:
            social_app = self.provedor.app
        except AttributeError:
            msg = f"Usuário {user.username} não possui provedor associado."
            LOGGER.error(msg)

        try:
            social_account = user.socialaccount_set.get(
                provider=self.provedor.app.provider_id
            )
        except SocialAccount.DoesNotExist:
            realm = self.provedor.app.provider_id
            msg = f"Usuário {user.username} não está associado ao realm {realm}."
            LOGGER.error(msg)
        except SocialAccount.MultipleObjectsReturned:
            msg = f"Usuário com mais de um provedor associado: {user.username}."

        access_token, refresh_token = self._obter_tokens(social_account)
        if access_token and refresh_token:
            self._enviar_req_logout(social_app, access_token, refresh_token)
        else:
            LOGGER.error("Erro ao obter tokens")

    def _enviar_req_logout(
        self, social_app: SocialApp, access_token: str, refresh_token: str
    ) -> None:
        """Envia requisição ao keycloak."""
        logout_request_data = {
            "client_id": social_app.client_id,
            "refresh_token": refresh_token,
            "client_secret": social_app.secret,
        }
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        requests.post(
            self.provedor.app.settings["logout_url"],
            data=logout_request_data,
            headers=headers,
        )

    def _obter_tokens(self, social_account: SocialAccount) -> tuple[str, str]:
        """Obtém tokens da conta que está deslogando."""
        social_token = social_account.socialtoken_set.order_by("-expires_at").first()
        access_token = social_token.token if social_token else ""
        refresh_token = social_token.token_secret if social_token else ""
        return (access_token, refresh_token)