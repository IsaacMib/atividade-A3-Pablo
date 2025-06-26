from links.models import LinkCabecalhoItemBlock
from django.conf import settings

def conteudo_site(request):
    return {
        "links_menu": LinkCabecalhoItemBlock.objects.all(),
    }

def versao_context(request):
    return {
        "SISTEMA_VERSAO": settings.SISTEMA_VERSAO,
        "AMBIENTE": settings.AMBIENTE,
    }