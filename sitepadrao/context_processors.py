from links.models import LinkCabecalhoItemBlock

def conteudo_site(request):
    return {
        "links_menu": LinkCabecalhoItemBlock.objects.all(),
    }