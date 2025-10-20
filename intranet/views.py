from django.shortcuts import render
from django.http import HttpResponse
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import GrupoIntranet
from django.contrib.auth import logout
from django.shortcuts import redirect

def intranet_dashboard(request):
    return HttpResponse("<h1>Painel de Gerenciamento da Intranet</h1>")

class GrupoIntranetViewSet(SnippetViewSet):
    model = GrupoIntranet
    menu_label = "Grupos da Intranet"
    icon = "group"
    list_display = ("nome",)
    search_fields = ("nome",)


def intranet_logout(request):
    logout(request)
    return redirect('/')
