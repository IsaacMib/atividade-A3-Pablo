from django.conf import settings

def versao_context(request):
    return {
        "SISTEMA_VERSAO": settings.SISTEMA_VERSAO,
        "AMBIENTE": settings.AMBIENTE,
        "HABILITAR_SSO_LOGIN": getattr(settings, 'HABILITAR_SSO_LOGIN', False),
    }