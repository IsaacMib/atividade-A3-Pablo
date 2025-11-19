from django import template
from dicas_presidente.models import DicasPresidentePage

register = template.Library()


@register.simple_tag
def ultimas_dicas_presidente(quantidade=3):
    """Retorna as últimas dicas do presidente."""
    return (
        DicasPresidentePage.objects.live()
        .order_by("-data_publicacao")[:quantidade]
    )


@register.simple_tag
def frase_aleatoria_presidente():
    """Retorna uma frase aleatória do presidente."""
    frases = (
        DicasPresidentePage.objects.live()
        .filter(tipo_dica='frase')
        .order_by('?')
    )
    return frases.first() if frases.exists() else None


@register.simple_tag
def buscar_dicas(tipo='todas', apenas_destaques=False, quantidade=6):
    """
    Busca dicas filtradas por tipo e/ou destaque.
    
    Args:
        tipo: Tipo de dica ('todas', 'mensagem', 'recomendacao', etc)
        apenas_destaques: Se True, retorna apenas dicas em destaque
        quantidade: Número máximo de dicas a retornar
    """
    dicas = DicasPresidentePage.objects.live()
    
    if tipo and tipo != 'todas':
        dicas = dicas.filter(tipo_dica=tipo)
    
    if apenas_destaques:
        dicas = dicas.filter(destaque=True)
    
    return dicas.order_by("-data_publicacao")[:quantidade]
