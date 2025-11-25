"""
StreamField blocks reutilizáveis para páginas do NEUROATHENA.

NOTA: HeroBlock e FeatureCardsBlock estão em blocks/home.py
      LocalizacaoBlock está em blocks/institucional.py
      Blocos de CorpoTecnico estão em blocks/corpo_tecnico.py
"""

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class TimelineEventBlock(blocks.StructBlock):
    """Um único evento do timeline."""
    
    ano = blocks.CharBlock(label="Ano", max_length=10, help_text="Ex: '2023', '2024'", required=False)
    titulo = blocks.CharBlock(label="Título", max_length=100)
    descricao = blocks.RichTextBlock(label="Descrição", features=['bold', 'italic', 'link'])
    
    class Meta:
        icon = "order"


class TimelineBlock(blocks.StructBlock):
    """Timeline de passos ou eventos históricos."""
    
    titulo = blocks.CharBlock(label="Título da Seção", max_length=200, required=False)
    eventos = blocks.ListBlock(
        TimelineEventBlock(),
        label="Eventos",
        min_num=2,
        max_num=10
    )
    
    class Meta:
        template = "blocks/timeline_block.html"
        icon = "list-ol"
        label = "Timeline"


class FAQItemBlock(blocks.StructBlock):
    """Um item de FAQ."""
    
    question = blocks.CharBlock(label="Pergunta", max_length=200)
    answer = blocks.RichTextBlock(label="Resposta", features=['bold', 'italic', 'link'])
    
    class Meta:
        icon = "help"


class FAQBlock(blocks.StructBlock):
    """Seção de perguntas frequentes."""
    
    title = blocks.CharBlock(label="Título da Seção", max_length=200, default="Perguntas Frequentes")
    items = blocks.ListBlock(
        FAQItemBlock(),
        label="Perguntas e Respostas",
        min_num=1
    )
    
    class Meta:
        template = "blocks/faq_block.html"
        icon = "help"
        label = "FAQ"


class CTASectionBlock(blocks.StructBlock):
    """Seção de Call-to-Action com botões e imagem de fundo."""
    
    titulo = blocks.CharBlock(label="Título", max_length=200)
    texto = blocks.RichTextBlock(label="Texto", features=['bold', 'italic'], required=False)
    link_primario = blocks.URLBlock(label="Link Botão Primário")
    texto_primario = blocks.CharBlock(label="Texto Botão Primário", max_length=50)
    link_secundario = blocks.URLBlock(label="Link Botão Secundário", required=False)
    texto_secundario = blocks.CharBlock(label="Texto Botão Secundário", max_length=50, required=False)
    imagem_fundo = ImageChooserBlock(label="Imagem de Fundo", required=False)
    
    class Meta:
        template = "blocks/cta_section_block.html"
        icon = "pick"
        label = "Call-to-Action"


class DepoimentoBlock(blocks.StructBlock):
    """Um único depoimento."""
    
    nome = blocks.CharBlock(label="Nome", max_length=100)
    cargo = blocks.CharBlock(label="Função/Cargo", max_length=100, required=False)
    foto = ImageChooserBlock(label="Foto", required=False)
    texto = blocks.TextBlock(label="Depoimento", max_length=500)
    
    class Meta:
        icon = "openquote"


class TestimonialBlock(blocks.StructBlock):
    """Seção de depoimentos de usuários."""
    
    titulo = blocks.CharBlock(label="Título da Seção", max_length=200, required=False)
    depoimentos = blocks.ListBlock(
        DepoimentoBlock(),
        label="Depoimentos",
        min_num=1,
        max_num=6
    )
    
    class Meta:
        template = "blocks/testimonial_block.html"
        icon = "openquote"
        label = "Depoimentos"


class EstatisticaBlock(blocks.StructBlock):
    """Um item de estatística."""
    
    numero = blocks.CharBlock(label="Número", max_length=20, help_text="Ex: '95%', '1000+'")
    label = blocks.CharBlock(label="Descrição", max_length=100)
    descricao = blocks.TextBlock(label="Descrição Detalhada", max_length=200, required=False)
    
    class Meta:
        icon = "order"


class StatisticsBlock(blocks.StructBlock):
    """Seção de estatísticas destacadas."""
    
    titulo = blocks.CharBlock(label="Título da Seção", max_length=200, required=False)
    estatisticas = blocks.ListBlock(
        EstatisticaBlock(),
        label="Estatísticas",
        min_num=2,
        max_num=6
    )
    
    class Meta:
        template = "blocks/statistics_block.html"
        icon = "order-up"
        label = "Estatísticas"


class ImageTextBlock(blocks.StructBlock):
    """Bloco de imagem com texto lado a lado."""
    
    imagem = ImageChooserBlock(label="Imagem")
    alinhamento = blocks.ChoiceBlock(
        label="Posição da Imagem",
        choices=[
            ('esquerda', 'Esquerda'),
            ('direita', 'Direita'),
        ],
        default='esquerda'
    )
    titulo = blocks.CharBlock(label="Título", max_length=200, required=False)
    texto = blocks.RichTextBlock(
        label="Texto",
        features=['h3', 'h4', 'bold', 'italic', 'link', 'ul', 'ol']
    )
    link = blocks.URLBlock(label="Link do Botão", required=False)
    texto_link = blocks.CharBlock(label="Texto do Botão", max_length=50, required=False)
    
    class Meta:
        template = "blocks/image_text_block.html"
        icon = "image"
        label = "Imagem + Texto"


class RichTextSectionBlock(blocks.StructBlock):
    """Seção simples de texto rico com todas as funcionalidades."""
    
    titulo = blocks.CharBlock(label="Título", max_length=200, required=False)
    conteudo = blocks.RichTextBlock(
        label="Conteúdo",
        features=['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ul', 'ol', 'hr', 'document-link', 'image', 'embed']
    )
    
    class Meta:
        template = "blocks/richtext_section_block.html"
        icon = "doc-full"
        label = "Seção de Texto Rico"
