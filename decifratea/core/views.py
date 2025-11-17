"""
Views do app Core.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import ConfiguracaoSistema, Log


def manutencao_view(request):
    """
    View exibida quando o sistema está em manutenção.
    """
    config = ConfiguracaoSistema.get_config()
    
    context = {
        'mensagem': config.mensagem_manutencao,
        'config': config,
    }
    
    return render(request, 'core/manutencao.html', context)


@login_required
def logs_view(request):
    """
    View para visualizar logs do sistema.
    Requer autenticação.
    """
    logs = Log.objects.all()[:100]  # Últimos 100 logs
    
    # Filtros
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        logs = logs.filter(tipo=tipo_filtro)
    
    context = {
        'logs': logs,
        'tipos': Log.TIPO_CHOICES,
    }
    
    return render(request, 'core/logs.html', context)


def health_check(request):
    """
    Endpoint de health check para monitoramento.
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Sistema operacional'
    })
