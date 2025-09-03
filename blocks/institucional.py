from wagtail.blocks import (
  CharBlock,
  StructBlock
)
from wagtail.images.blocks import ImageChooserBlock

import re


class LocalizacaoBlock(StructBlock):
    titulo_secao_localizacao = CharBlock(
        max_length=255,
        help_text="Título da seção de localização",
        default="Localização",
        required=True
    )

    nome_local = CharBlock(
        max_length=255,
        help_text="Nome do local",
        required=True
    )
    endereco = CharBlock(
        max_length=255,
        help_text="Endereço completo",
        required=True
    )
    cep = CharBlock(
        max_length=40,
        help_text="CEP",
        required=True
    )
    telefone = CharBlock(
        max_length=40,
        help_text="Número de telefone",
        required=True
    )
    horario_atendimento = CharBlock(
        max_length=100,
        help_text="Horário de atendimento. Ex.: das 8h às 16h30",
        required=True
    )
    imagem = ImageChooserBlock(
        required=False,
        help_text="Imagem do local (opcional)"
    )

    titulo_secao_mapa = CharBlock(
        max_length=255,
        help_text="Título da seção antes do mapa",
        default="Como Chegar",
        required=True
    )

    iframe_google_maps = CharBlock(
        required=True,
        label="HTML do Google Maps (iframe)",
        help_text="Cole aqui o código HTML do iframe fornecido pelo Google Maps (menu Compartilhar > Incorporar um mapa)."
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        iframe_html = value.get('iframe_google_maps', '')
        # Regex para extrair o src do iframe
        match = re.search(r'src="([^"]+)"', iframe_html)
        src_url = match.group(1) if match else ''
        context['maps_src'] = src_url
        # Usa os valores definidos pelo usuário
        context['maps_width'] = value.get('largura') or '100%'
        context['maps_height'] = value.get('altura') or '400'
        return context

    class Meta:
        icon = "site"
        label = "Localização"
        template = "blocks/localizacao.html"

class GoogleMapsEmbedBlock(StructBlock):
    iframe_html = CharBlock(
        required=True,
        label="HTML do Google Maps (iframe)",
        help_text="Cole aqui o código HTML do iframe fornecido pelo Google Maps (menu Compartilhar > Incorporar um mapa)."
    )
    largura = CharBlock(
        required=False,
        default="100%",
        label="Largura",
        help_text="Exemplo: 100% ou 600"
    )
    altura = CharBlock(
        required=False,
        default="400",
        label="Altura",
        help_text="Exemplo: 400"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        iframe_html = value.get('iframe_html', '')
        # Regex para extrair o src do iframe
        match = re.search(r'src="([^"]+)"', iframe_html)
        src_url = match.group(1) if match else ''
        context['maps_src'] = src_url
        # Usa os valores definidos pelo usuário
        context['maps_width'] = value.get('largura') or '100%'
        context['maps_height'] = value.get('altura') or '400'
        return context

    class Meta:
        icon = "site"
        label = "Google Maps"
        template = "blocks/google_maps_embed.html"