from django import template

register = template.Library()


@register.inclusion_tag("tags/aviso_administrador.html", takes_context=True)
def aviso_administrador(context, mensagem=None, tipo="info"):
    """
    Exibe um aviso visível apenas para usuários autenticados (administradores).
    
    Args:
        context: Contexto do template
        mensagem: Mensagem customizada (opcional)
        tipo: Tipo do alert Bootstrap - 'info', 'warning', 'danger', 'success' (padrão: 'info')
    
    Uso:
        {% load page_utils %}
        {% aviso_administrador %}
        {% aviso_administrador mensagem="Esta é uma mensagem customizada" tipo="warning" %}
    """
    request = context.get('request')
    
    # Só exibe se o usuário estiver autenticado
    if not request or not request.user.is_authenticated:
        return {
            'mostrar_aviso': False
        }
    
    # Mensagem padrão se nenhuma for fornecida
    if not mensagem:
        mensagem = "Esta página está sendo exibida porque você está autenticado no sistema."
    
    return {
        'mostrar_aviso': True,
        'mensagem': mensagem,
        'tipo': tipo,
        'user': request.user,
    }
