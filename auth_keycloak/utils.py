from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
)

from django.contrib.auth import get_user_model

UserModel = get_user_model()

def obter_provedor_recente(user: UserModel) -> OpenIDConnectProvider | None:
    """Obtém provedor usado no login"""
    if not user.is_authenticated:
        provedor = None
    else:
        social_account = user.socialaccount_set.order_by("-last_login").first()
        provedor = social_account.get_provider() if social_account else None
    return provedor