from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth import logout
from django.conf import settings
import logging

# Imports necessários para o logout do SSO
try:
    from auth_keycloak.utils import obter_provedor_recente, logout_sso, pode_fazer_logout_sso
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
            if pode_fazer_logout_sso(user, provedor):
                logout_sso(user, provedor)
        except Exception as e:
            LOGGER.error(f"Erro ao fazer logout do SSO: {e}")
    
    # Faz logout local do Django
    logout(request)
    
    # Redireciona para a página de login
    return redirect('/admin/login/')

def intranet_logout(request):
    """View de logout customizada que aceita GET."""
    user = request.user
    
    # Se SSO está habilitado e disponível, tenta fazer logout do SSO
    if settings.HABILITAR_SSO_LOGIN and SSO_AVAILABLE and user.is_authenticated:
        try:
            provedor = obter_provedor_recente(user)
            if pode_fazer_logout_sso(user, provedor):
                logout_sso(user, provedor)
        except Exception as e:
            LOGGER.error(f"Erro ao fazer logout do SSO: {e}")
    
    # Faz logout local do Django
    logout(request)
    
    # Redireciona para a página de login com next apontando para a home
    return redirect('/')
