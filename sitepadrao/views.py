from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth import logout
from django.conf import settings
import logging

# Imports necessários para o logout do SSO
try:
    from auth_keycloak.utils import obter_provedor_recente
    from allauth.socialaccount.models import SocialAccount, SocialApp
    import requests
    SSO_AVAILABLE = True
except ImportError:
    SSO_AVAILABLE = False

LOGGER = logging.getLogger(__name__)

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

def redirect_if_in_group(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.exists()):
        return redirect('/admin/manager/')
    return redirect('/')

def acesso_negado(request):
    return render(request, "403.html", status=403)

def erro_404(request, exception):
    return render(request, "404.html", status=404)

def erro_403(request, exception):
    return render(request, "403.html", status=403)

def wagtail_logout_with_sso(request):
    """View customizada para logout do Wagtail admin que também faz logout do SSO."""
    user = request.user
    
    # Se SSO está habilitado e disponível, tenta fazer logout do SSO
    if settings.HABILITAR_SSO_LOGIN and SSO_AVAILABLE and user.is_authenticated:
        try:
            provedor = obter_provedor_recente(user)
            if (
                provedor
                and provedor.app
                and "logout_url" in provedor.app.settings
                and provedor.app.settings["logout_url"] != ""
            ):
                _logout_sso(user, provedor)
        except Exception as e:
            LOGGER.error(f"Erro ao fazer logout do SSO: {e}")
    
    # Faz logout local do Django
    logout(request)
    
    # Redireciona para a página de login
    return redirect('/admin/login/')

def _logout_sso(user, provedor):
    """Faz logout do SSO usando a mesma lógica do KeycloakAdapter."""
    try:
        social_app = provedor.app
    except AttributeError:
        msg = f"Usuário {user.username} não possui provedor associado."
        LOGGER.error(msg)
        return

    try:
        social_account = user.socialaccount_set.get(
            provider=provedor.app.provider_id
        )
    except SocialAccount.DoesNotExist:
        realm = provedor.app.provider_id
        msg = f"Usuário {user.username} não está associado ao realm {realm}."
        LOGGER.error(msg)
        return
    except SocialAccount.MultipleObjectsReturned:
        msg = f"Usuário com mais de um provedor associado: {user.username}."
        LOGGER.warning(msg)
        # Pega o mais recente
        social_account = user.socialaccount_set.filter(
            provider=provedor.app.provider_id
        ).order_by("-last_login").first()

    access_token, refresh_token = _obter_tokens(social_account)
    if access_token and refresh_token:
        _enviar_req_logout(social_app, access_token, refresh_token)
    else:
        LOGGER.error("Erro ao obter tokens para logout do SSO")

def _enviar_req_logout(social_app, access_token, refresh_token):
    """Envia requisição ao keycloak para logout."""
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
        if response.status_code != 204:
            LOGGER.warning(f"Logout do SSO retornou status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Erro na requisição de logout do SSO: {e}")

def _obter_tokens(social_account):
    """Obtém tokens da conta que está deslogando."""
    if not social_account:
        return "", ""
    
    social_token = social_account.socialtoken_set.order_by("-expires_at").first()
    access_token = social_token.token if social_token else ""
    refresh_token = social_token.token_secret if social_token else ""
    return (access_token, refresh_token)
