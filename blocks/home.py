"""
Blocos específicos para a HomePage do NEUROATHENA.
"""

from wagtail.blocks import (
    StructBlock,
    CharBlock,
    TextBlock,
    URLBlock,
    ListBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class HeroBlock(StructBlock):
    """
    Bloco Hero principal da homepage com título, subtítulo, descrição e CTAs.
    """
    titulo = CharBlock(
        required=True,
        max_length=100,
        help_text="Título principal do hero (ex: NEUROATHENA)"
    )
    
    subtitulo = CharBlock(
        required=True,
        max_length=200,
        help_text="Subtítulo descritivo (ex: Sistema Multimodal de Triagem...)"
    )
    
    descricao = TextBlock(
        required=True,
        max_length=500,
        help_text="Descrição detalhada do sistema"
    )
    
    cta_primario_texto = CharBlock(
        required=False,
        max_length=50,
        default="Acessar Painel",
        help_text="Texto do botão principal"
    )
    
    cta_primario_url = URLBlock(
        required=False,
        default="/painel/",
        help_text="URL do botão principal"
    )
    
    cta_secundario_texto = CharBlock(
        required=False,
        max_length=50,
        default="Admin Wagtail",
        help_text="Texto do botão secundário"
    )
    
    cta_secundario_url = URLBlock(
        required=False,
        default="/cms/",
        help_text="URL do botão secundário"
    )
    
    class Meta:
        icon = 'home'
        label = 'Hero Principal'
        template = 'blocks/hero_home.html'


class FeatureCardBlock(StructBlock):
    """
    Card individual de funcionalidade/recurso.
    """
    icone = CharBlock(
        required=True,
        max_length=10,
        help_text="Emoji do ícone (ex: 🧠, 📊, 👥)"
    )
    
    titulo = CharBlock(
        required=True,
        max_length=100,
        help_text="Título da funcionalidade"
    )
    
    descricao = TextBlock(
        required=True,
        max_length=300,
        help_text="Descrição breve da funcionalidade"
    )
    
    class Meta:
        icon = 'snippet'
        label = 'Card de Funcionalidade'


class FeaturesGridBlock(StructBlock):
    """
    Grid de funcionalidades/recursos do sistema.
    """
    titulo_secao = CharBlock(
        required=True,
        max_length=100,
        default="Recursos Principais",
        help_text="Título da seção de funcionalidades"
    )
    
    funcionalidades = ListBlock(
        FeatureCardBlock(),
        min_num=1,
        max_num=9,
        help_text="Cards de funcionalidades (recomendado: 3, 6 ou 9 para grid)"
    )
    
    class Meta:
        icon = 'th'
        label = 'Grid de Funcionalidades'
        template = 'blocks/features_grid.html'


class CTABlock(StructBlock):
    """
    Seção de Call-to-Action (chamada para ação).
    """
    titulo = CharBlock(
        required=True,
        max_length=150,
        help_text="Título da seção CTA"
    )
    
    descricao = TextBlock(
        required=True,
        max_length=500,
        help_text="Descrição/texto persuasivo"
    )
    
    botao_texto = CharBlock(
        required=True,
        max_length=50,
        help_text="Texto do botão de ação"
    )
    
    botao_url = URLBlock(
        required=True,
        help_text="URL de destino do botão"
    )
    
    imagem_fundo = ImageChooserBlock(
        required=False,
        help_text="Imagem de fundo opcional para a seção"
    )
    
    class Meta:
        icon = 'pick'
        label = 'Call-to-Action (CTA)'
        template = 'blocks/cta_home.html'
