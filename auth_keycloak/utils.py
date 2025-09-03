import logging
import requests
from typing import Optional, Tuple
from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
)
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.auth import get_user_model

LOGGER = logging.getLogger(__name__)
UserModel = get_user_model()

def obter_provedor_recente(user) -> Optional[OpenIDConnectProvider]:
    """Obtém provedor usado no login"""
    if not user.is_authenticated:
        provedor = None
    else:
        social_account = user.socialaccount_set.order_by("-last_login").first()
        provedor = social_account.get_provider() if social_account else None
    return provedor

def logout_sso(user, provedor: OpenIDConnectProvider) -> bool:
    """
    Faz logout do SSO usando o provedor fornecido.
    
    Args:
        user: Usuário que está fazendo logout
        provedor: Provedor OpenID Connect configurado
        
    Returns:
        bool: True se o logout foi bem-sucedido, False caso contrário
    """
    try:
        social_app = provedor.app
    except AttributeError:
        msg = f"Usuário {user.username} não possui provedor associado."
        LOGGER.error(msg)
        return False

    try:
        social_account = user.socialaccount_set.get(
            provider=provedor.app.provider_id
        )
    except SocialAccount.DoesNotExist:
        realm = provedor.app.provider_id
        msg = f"Usuário {user.username} não está associado ao realm {realm}."
        LOGGER.error(msg)
        return False
    except SocialAccount.MultipleObjectsReturned:
        msg = f"Usuário com mais de um provedor associado: {user.username}."
        LOGGER.warning(msg)
        # Pega o mais recente
        social_account = user.socialaccount_set.filter(
            provider=provedor.app.provider_id
        ).order_by("-last_login").first()

    access_token, refresh_token = _obter_tokens(social_account)
    if access_token and refresh_token:
        return _enviar_req_logout(social_app, access_token, refresh_token)
    else:
        LOGGER.error("Erro ao obter tokens para logout do SSO")
        return False

def pode_fazer_logout_sso(user, provedor: Optional[OpenIDConnectProvider]) -> bool:
    """
    Verifica se é possível fazer logout do SSO para o usuário.
    
    Args:
        user: Usuário a ser verificado
        provedor: Provedor OpenID Connect
        
    Returns:
        bool: True se pode fazer logout do SSO, False caso contrário
    """
    return (
        provedor
        and provedor.app
        and "logout_url" in provedor.app.settings
        and provedor.app.settings["logout_url"] != ""
        and user.is_authenticated
    )

def _enviar_req_logout(social_app: SocialApp, access_token: str, refresh_token: str) -> bool:
    """
    Envia requisição ao keycloak para logout.
    
    Args:
        social_app: App social configurada
        access_token: Token de acesso
        refresh_token: Token de refresh
        
    Returns:
        bool: True se o logout foi bem-sucedido, False caso contrário
    """
    logout_request_data = {
        "client_id": social_app.client_id,
        "refresh_token": refresh_token,
        "client_secret": social_app.secret,
    }
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            social_app.settings["logout_url"],
            data=logout_request_data,
            headers=headers,
            timeout=10  # timeout para evitar travamento
        )
        if response.status_code == 204:
            LOGGER.info("Logout do SSO realizado com sucesso")
            return True
        else:
            LOGGER.warning(f"Logout do SSO retornou status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Erro na requisição de logout do SSO: {e}")
        return False

def _obter_tokens(social_account: SocialAccount) -> Tuple[str, str]:
    """
    Obtém tokens da conta que está deslogando.
    
    Args:
        social_account: Conta social do usuário
        
    Returns:
        tuple: (access_token, refresh_token)
    """
    if not social_account:
        return "", ""
    
    social_token = social_account.socialtoken_set.order_by("-expires_at").first()
    access_token = social_token.token if social_token else ""
    refresh_token = social_token.token_secret if social_token else ""
    return (access_token, refresh_token)