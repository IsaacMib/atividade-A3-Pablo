from blocks.utils import (
    ICONES_REDES,
    ICONES_ACESSO_RAPIDO,
    IDS_METABASE_CARDS,
    CLASS_TITULO_BG_COLOR_BLOCK,
    GRID_IMAGENS_TYPES,
    GRID_IMAGENS_CLASSES,
    GRID_IMAGENS_DEFAULT_TYPE,
    BANNER_MODES,
    BANNER_SIZES,
    get_metabase_card_text_by_id,
    validate_file_size
)

from django.db import models

import re
import requests
import re
from django.core.cache import cache
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    ListBlock,
    FloatBlock,
    PageChooserBlock,
    URLBlock,
    IntegerBlock,
    BooleanBlock,
    PageChooserBlock,
    DateBlock,
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.embeds.blocks import EmbedBlock
from django.utils.functional import cached_property
from wagtail.images import get_image_model
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.conf import settings

import uuid

import magic
from django.utils.html import format_html_join
from django.db import models
from .forms import (
    SingleLineFieldBlock,
    MultiLineFieldBlock,
    EmailFieldBlock,
    NumberFieldBlock,
    FileFieldBlock,
)

from django.core.exceptions import ValidationError

mappingIconsServicos = {
    'HIBRIDO': 'icon: link; ratio: 0.75',
    'PRESENCIAL': 'icon: user; ratio: 0.75',
    'ONLINE': 'icon: desktop; ratio: 0.75',
    'PRESENCIAL_AGENDAMENTO': 'icon: calendar; ratio: 0.75',
}

_CACHE_TIMEOUT = 10*60  # 10 minutos em segundos


class AcessoRapidoItemBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100)
    link = URLBlock(required=True)
    icone = ChoiceBlock(choices=ICONES_ACESSO_RAPIDO,
                        required=True, label="Ícone")

    class Meta:
        icon = 'link'
        label = "Item de Acesso Rápido"


class AcessosRapidosBlock(StructBlock):
    titulo = CharBlock(required=False, default="Acessos Rápidos")
    itens = ListBlock(AcessoRapidoItemBlock(), default=[])

    class Meta:
        icon = "list-ul"
        label = "Bloco de Acessos Rápidos"
        template = "blocks/list_acesso_rapido.html"


class AcessoRapidoWidget(StructBlock):
    titulo = CharBlock(
        required=False,
        default="Acessos Rápidos",
        help_text="Título exibido acima dos acessos rápidos"
    )
    itens = ListBlock(AcessoRapidoItemBlock(), default=[])

    class Meta:
        icon = "list-ul"
        label = "Widget de Acessos Rápidos"
        template = "blocks/widget_acesso_rapido.html"



class ImagemConfiguracao(blocks.StructBlock):
    """Bloco para configuração de imagem com suas propriedades de renderização"""
    imagem = ImageChooserBlock(
        required=True,
        label="Imagem"
    )
    mode = blocks.ChoiceBlock(
        choices=BANNER_MODES,
        default='fill',
        label="Modo de Ajuste",
        help_text="Define como a imagem será ajustada ao tamanho escolhido."
    )
    size = blocks.ChoiceBlock(
        choices=BANNER_SIZES,
        default='1920x1080',
        label="Tamanho",
        help_text="Selecione o tamanho desejado."
    )

    class Meta:
        label = "Configuração de Imagem"
        icon = "image"


class ImagemMobileConfiguracao(blocks.StructBlock):
    """Bloco para configuração de imagem mobile com suas propriedades de renderização"""
    imagem = ImageChooserBlock(
        required=False,
        label="Imagem"
    )
    mode = blocks.ChoiceBlock(
        choices=BANNER_MODES,
        default='fill',
        label="Modo de Ajuste",
        help_text="Define como a imagem será ajustada ao tamanho escolhido."
    )
    size = blocks.ChoiceBlock(
        choices=BANNER_SIZES,
        default='1920x1080',
        label="Tamanho",
        help_text="Selecione o tamanho desejado."
    )

    class Meta:
        label = "Configuração de Imagem Mobile"
        icon = "mobile"


class BannerComLinkBlock(blocks.StructBlock):
    # Configurações de imagem agrupadas
    imagem_desktop = ImagemConfiguracao(
        label="🖥️ Configuração Desktop/Tablet",
        help_text="Configurações da imagem que será exibida em desktops e tablets."
    )
    imagem_mobile = ImagemMobileConfiguracao(
        required=False,
        label="📱 Configuração Mobile (Opcional)",
        help_text="Configurações da imagem alternativa para dispositivos menores. Se não preenchido, usará a configuração desktop."
    )
    
    link = blocks.URLBlock(
        required=True,
        label="URL do Banner"
    )
    alt_texto = blocks.CharBlock(
        required=False,
        label="Texto alternativo",
        help_text="Descrição curta para acessibilidade e SEO."
    )
    abrir_nova_aba = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Abrir em nova aba?"
    )
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        
        # Configurações da imagem desktop
        imagem_desktop_config = value.get('imagem_desktop', {})
        imagem_desktop = imagem_desktop_config.get('imagem')
        mode_desktop = imagem_desktop_config.get('mode', 'fill')
        size_desktop = imagem_desktop_config.get('size', '1920x1080')
        
        # Configurações da imagem mobile
        imagem_mobile_config = value.get('imagem_mobile', {})
        imagem_mobile = imagem_mobile_config.get('imagem') if imagem_mobile_config else None
        mode_mobile = imagem_mobile_config.get('mode', mode_desktop) if imagem_mobile_config else mode_desktop
        size_mobile = imagem_mobile_config.get('size', size_desktop) if imagem_mobile_config else size_desktop
        
        # Processa imagem desktop
        if imagem_desktop:
            # Se mode E size forem original → não faz alteração alguma
            if mode_desktop == "original" and size_desktop == "original":
                context['rendition_desktop'] = None
            # Se apenas size for original → não faz redimensionamento mesmo com modo selecionado
            elif size_desktop == "original":
                context['rendition_desktop'] = None
            # Se apenas mode for original → usa o size selecionado para redimensionar
            elif mode_desktop == "original":
                try:
                    # Usa apenas o tamanho para redimensionar (sem modo específico - usa 'max' como padrão)
                    filter_spec = f"max-{size_desktop}"
                    context['rendition_desktop'] = imagem_desktop.get_rendition(filter_spec)
                except Exception as e:
                    # Em caso de erro, deixa como None para usar a imagem original
                    context['rendition_desktop'] = None
            # Mode e size normais → aplica filtro completo
            else:
                try:
                    filter_spec = f"{mode_desktop}-{size_desktop}"
                    context['rendition_desktop'] = imagem_desktop.get_rendition(filter_spec)
                except Exception as e:
                    # Em caso de erro, deixa como None para usar a imagem original
                    context['rendition_desktop'] = None
        else:
            context['rendition_desktop'] = None
        
        # Processa imagem mobile
        if imagem_mobile:
            # Se mode E size forem original → não faz alteração alguma
            if mode_mobile == "original" and size_mobile == "original":
                context['rendition_mobile'] = None
            # Se apenas size for original → não faz redimensionamento mesmo com modo selecionado
            elif size_mobile == "original":
                context['rendition_mobile'] = None
            # Se apenas mode for original → usa o size selecionado para redimensionar
            elif mode_mobile == "original":
                try:
                    # Usa apenas o tamanho para redimensionar (sem modo específico - usa 'max' como padrão)
                    filter_spec = f"max-{size_mobile}"
                    context['rendition_mobile'] = imagem_mobile.get_rendition(filter_spec)
                except Exception as e:
                    # Em caso de erro, deixa como None para usar a imagem original
                    context['rendition_mobile'] = None
            # Mode e size normais → aplica filtro completo
            else:
                try:
                    filter_spec = f"{mode_mobile}-{size_mobile}"
                    context['rendition_mobile'] = imagem_mobile.get_rendition(filter_spec)
                except Exception as e:
                    # Em caso de erro, deixa como None para usar a imagem original
                    context['rendition_mobile'] = None
        else:
            context['rendition_mobile'] = None
        
        return context

    def clean(self, value):
        cleaned_data = super().clean(value)
        
        # Validação básica: verificar se pelo menos a imagem desktop está configurada
        imagem_desktop_config = cleaned_data.get('imagem_desktop', {})
        if not imagem_desktop_config.get('imagem'):
            raise ValidationError('A imagem para desktop é obrigatória.')

        return cleaned_data

    class Meta:
        icon = "image"
        label = "Banner com Link"
        template = "blocks/banner.html"

class VideoBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100)
    srcIframe = URLBlock(required=True, label="URL do vídeo (iframe YouTube)")

    def get_context(self, value, parent_context=None):
        YOUTUBE_NOCOOKIE_EMBED_URL = "https://www.youtube-nocookie.com/embed/"
        YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v="

        context = super().get_context(value, parent_context=parent_context)
        url = value.get('srcIframe') or ''

        # Normaliza vários formatos de URL do YouTube para URL de embed segura (nocookie)
        video_id = None
        # YouTube URL patterns with named constants
        YOUTUBE_BE_PATTERN = (r'youtu\.be/([^#\&\?]*)', 1)  # youtu.be/ID
        YOUTUBE_EMBED_PATTERN = (r'/embed/([^#\&\?/]*)', 1)  # youtube.com/embed/ID
        YOUTUBE_SHORTS_PATTERN = (r'/shorts/([^#\&\?/]*)', 1)  # youtube.com/shorts/ID
        YOUTUBE_WATCH_PATTERN = (r'[?&]v=([^#\&\?]*)', 1)  # youtube.com/watch?v=ID

        # Try each pattern in order
        for pattern, group in [
            YOUTUBE_BE_PATTERN,
            YOUTUBE_EMBED_PATTERN,
            YOUTUBE_SHORTS_PATTERN,
            YOUTUBE_WATCH_PATTERN
        ]:
            match = re.search(pattern, url, re.IGNORECASE)
            if match and match.group(group):
                video_id = match.group(group)
                break
        else:
            video_id = None

        # Monta src de embed com domínio de privacidade; mantém alguns params úteis
        if video_id:
            base = f"{YOUTUBE_NOCOOKIE_EMBED_URL}{video_id}"
            params = []
            # parâmetros padrão recomendados
            params.extend(["rel=0", "modestbranding=1"])
            # preserva start (início em segundos) se existir
            try:
                from urllib.parse import urlparse, parse_qs
                start_qs = parse_qs(urlparse(url).query or '')
                if 'start' in start_qs:
                    params.append(f"start={start_qs['start'][0]}")
                if 't' in start_qs:  # suporte a t=1m30s não convertido aqui
                    params.append(f"t={start_qs['t'][0]}")
            except Exception:
                pass
            src = base + (('?' + '&'.join(params)) if params else '')
            watch_url = f"{YOUTUBE_WATCH_URL}{video_id}"
        else:
            # fallback: usa URL original
            src = url
            watch_url = url

        context['titulo'] = value.get('titulo')
        context['src'] = src
        context['watch_url'] = watch_url
        return context

    class Meta:
        icon = 'media'
        label = "Vídeo"
        template = 'blocks/video.html'


class ListaVideosBlock(StructBlock):
    titulo = CharBlock(required=False, default="Vídeos")
    ver_todos_url = URLBlock(required=False, label="URL do 'Ver todos'")
    videos = ListBlock(VideoBlock(), label="Vídeos", max_num=3)

    class Meta:
        icon = 'list-ul'
        label = "Lista de Vídeos"
        template = 'blocks/list_video.html'


class RedeSocialItemBlock(StructBlock):
    nome = CharBlock(required=True)
    link = URLBlock(required=True)
    icone = ChoiceBlock(choices=ICONES_REDES, required=True)

    class Meta:
        icon = "site"
        label = "Bloco de Redes Sociais"
        template = "blocks/redes_sociais.html"


class ListRedeSocial(StructBlock):
    titulo = CharBlock(required=False, default="Siga-nos nas redes sociais")
    imagem = ImageChooserBlock(
        required=False, help_text="Imagem que será exibida ao lado do texto.")
    redes = ListBlock(RedeSocialItemBlock(), max_num=4)

    class Meta:
        icon = 'list-ul'
        label = "Lista de Redes Sociais"
        template = "blocks/redes_sociais.html"

class ListRedesSocial(StructBlock):

    ICONES_REDES = [
        ("facebook", "Facebook"),
        ("x", "X (Twitter)"),
        ("linkedin", "LinkedIn"),
        ("whatsapp", "WhatsApp"),
        ("telegram", "Telegram"),
        ("email", "E-mail"),
        ("sms", "SMS"),
        ("print", "Imprimir"),
        ("copy", "Copiar Link"),
        ("reddit", "Reddit"),
        ("pinterest", "Pinterest"),
        ("messenger", "Messenger"),
    ]

    redes = ListBlock(
        ChoiceBlock(choices=ICONES_REDES, label="Rede de compartilhamento"),
        label="Selecionar Redes de Compartilhamento",
        help_text="Selecione as redes sociais nas quais o conteúdo poderá ser compartilhado."
    )

    class Meta:
        icon = "share"
        label = "Compartilhamento em Redes Sociais"
        template = "blocks/redes_sociais_share.html"

class ItemCarrosselBannerBlock(StructBlock):
    imagem = ImageChooserBlock(required=True, label="Imagem do Banner")
    imagem_mobile = ImageChooserBlock(
        required=False,
        label="Imagem do Banner para Celulares e Telas Menores",
        help_text="Imagem que será exibida em telas menores (ex: celulares)")
    link = URLBlock(required=False, label="URL do Banner")
    texto_alternativo = CharBlock(
        required=False,
        label="Texto alternativo",
        help_text="Descrição da imagem para acessibilidade (alt text)"
    )
    legenda = CharBlock(
        required=False,
        label="Legenda do Banner",
        help_text="Texto que aparece sobre o banner (opcional)"
    )

    class Meta:
        icon = 'image'
        label = "Item do Carrossel"
        template = 'blocks/item_carrossel_banner.html'


class CarrosselBannersBlock(StructBlock):
    banners = ListBlock(
        ItemCarrosselBannerBlock(),
        label="Banners",
        help_text="Adicione os banners para o carrossel"
    )

    class Meta:
        icon = 'image'
        label = "Carrossel de Banners"
        template = 'blocks/carrossel_banners.html'


class ServicoOnlineItemBlock(StructBlock):
    idServico = CharBlock(required=False, label="ID do Serviço")

    def parserDadosApiServico(self, item):
        """
        Função para tratar/parsear um único item retornado pela API de serviços online.
        Retorna um dicionário com os campos esperados por ServicoOnlineItemBlock.
        O campo 'modalidades' será um array de objetos com 'iconClass' e 'nome'.
        """
        modalidades = []
        for fp in item.get('formas_prestacao', []):
            forma = fp.get('forma_prestacao')
            if forma:
                modalidades.append({
                    'iconClass': self.getIconClass(forma),
                    'nome': forma
                })
        return {
            'sigla': item.get('orgao', {}).get('sigla', ''),
            'titulo': item.get('categoria', {}),
            'descricao': item.get('nome', ''),
            'link': f"{settings.PORTAL_SERVICOS_URL}{item.get('id', '')}",
            'modalidades': modalidades,
            'observacao': item.get('o_que_e', ''),
        }

    def get_context(self, value, parent_context=None):
        import requests
        context = super().get_context(value, parent_context=parent_context)
        api_url = f"{settings.PORTAL_SERVICOS_API_URL}digital/servicos/{value.get('idServico', '')}"
        servico = []
        try:
            response = requests.get(api_url, timeout=5)
            if response.ok:
                servico = self.parserDadosApiServico(response.json())
        except Exception:
            servico = []
        context['servico'] = servico
        return context

    def getIconClass(self, modalidade):
        """
        Retorna a string do ícone correspondente à modalidade.
        """
        return mappingIconsServicos.get(str(modalidade).upper(), 'icon: question; ratio: 0.75')

    class Meta:
        icon = 'form'
        label = "Item de Serviço Online"
        template = 'blocks/item_servico_online.html'


class ServicosOnlineBlock(StructBlock):
    titulo = CharBlock(
        required=True,
        default="Serviços Online",
        help_text="Título que aparecerá acima da lista de serviços"
    )
    orgao_sigla = CharBlock(
        required=True,
        label="Órgão (sigla)",
        help_text="Sigla do órgão para consulta na API.Ex.: detran,sead,codata, etc."
    )
    limit = IntegerBlock(
        required=False,
        default=12,
        min_value=1,
        label="Limite de serviços exibidos",
        help_text="Número máximo de serviços a serem exibidos no carrossel. Padrão é 12."
    )

    def parserDadosApiServico(self, dados):
        """
        Função para tratar/parsear os dados retornados pela API de serviços online.
        Monta um novo array de dicionários com os campos esperados por ServicoOnlineItemBlock.
        O campo 'modalidades' será um array de objetos com 'iconClass' e 'nome'.
        """
        resultado = []
        for item in dados:
            modalidades = []
            for fp in item.get('formas_prestacao', []):
                forma = fp.get('forma_prestacao')
                if forma:
                    modalidades.append({
                        'iconClass': self.getIconClass(forma),
                        'nome': forma
                    })
            resultado.append({
                'sigla': item.get('orgao', {}).get('sigla', ''),
                'titulo': item.get('categoria', {}).get('nome', ''),
                'descricao': item.get('nome', ''),
                'link': f"{settings.PORTAL_SERVICOS_URL}{item.get('id', '')}",
                'modalidades': modalidades,
                'observacao': item.get('o_que_e', ''),
            })
        return resultado

    def get_context(self, value, parent_context=None):
        import requests
        context = super().get_context(value, parent_context=parent_context)
        orgao_sigla = value.get('orgao_sigla')
        order_by = '-contador_acesso'
        limit = value.get('limit') or 12
        api_url = f"{settings.PORTAL_SERVICOS_API_URL}digital/servicos/orgao/"
        servicos = []
        linkTodos = f"{settings.PORTAL_SERVICOS_URL}"
        if api_url and orgao_sigla:
            params = {
                'orgao_sigla': orgao_sigla.lower(),
                'order_by': order_by,
                'limit': limit
            }
            try:
                response = requests.get(api_url, params=params, timeout=5)
                if response.ok:
                    dados = response.json()
                    servicos = self.parserDadosApiServico(dados)
                    linkTodos = f"{settings.PORTAL_SERVICOS_URL}todos?orgao={dados[0].get('orgao', {}).get('id', '')}&page=0"
            except Exception:
                servicos = []
        context['servicos'] = servicos
        context['linkTodos'] = linkTodos
        return context

    def getIconClass(self, modalidade):
        """
        Retorna a string do ícone correspondente à modalidade.
        """
        return mappingIconsServicos.get(str(modalidade).upper(), 'icon: question; ratio: 0.75')

    class Meta:
        icon = 'list-ul'
        label = 'Carrossel de Serviços Online'
        template = 'blocks/servicos_online.html'


class TituloBlock(StructBlock):

    """Bloco de título com opções de estilo e visibilidade."""

    titulo = CharBlock(
        required=True,
        help_text='Digite o título que será exibido'
    )

    corBackground = ChoiceBlock(
        choices=CLASS_TITULO_BG_COLOR_BLOCK,
        required=False,
        label="Cor de Fundo",
        default='titulo-bg-default'
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        return context

    class Meta:
        template = 'blocks/titulo.html'
        icon = 'title'
        label = 'Título'


class OdometerBlock(StructBlock):
    odometer_value = FloatBlock(required=False, label="Valor do Dado Default",
                                help_text="Preenchido automaticamente pela API", disabled=True)
    id_card = ChoiceBlock(
        required=True,
        label="ID do Card do Metabase",
        choices=IDS_METABASE_CARDS,
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        id_card = value['id_card']
        id_card_text = get_metabase_card_text_by_id(id_card)
        url = f"{settings.METABASE_API_URL}{id_card}"
        headers = {
            'x-api-key': settings.METABASE_API_KEY
        }
        cache_key = f"metabase_odometer_value_{id_card}"
        data = cache.get(cache_key)
        if data is None:
            try:
                response = requests.get(url, headers=headers)
                if response.ok:
                    response_json = response.json()
                    result_metadata = response_json.get('result_metadata', [])
                    if result_metadata:
                        metabase_value = result_metadata[0].get('fingerprint', {}).get(
                            'type', {}).get('type/Number', {}).get('q1', 0)
                    else:
                        metabase_value = value['odometer_value']
                else:
                    metabase_value = value['odometer_value']
                cache.set(cache_key, metabase_value, timeout=_CACHE_TIMEOUT)
            except Exception as e:
                metabase_value = value['odometer_value']
        else:
            metabase_value = data
        context['self'].metabase_value = metabase_value
        context['id_card'] = id_card
        context['id_card_text'] = id_card_text
        context['uuid'] = str(uuid.uuid4())
        return context

    class Meta:
        template = 'blocks/odometer.html'
        icon = 'plus'
        label = 'Odometer'


class OdometerListBlock(StructBlock):
    titulo = CharBlock(
        required=False,
        default="Central de Monitoramento",
        help_text="Título que aparecerá acima da lista de odômetros"
    )
    odometers = ListBlock(OdometerBlock(), label="Central de Monitoramento")

    class Meta:
        template = 'blocks/central_monitoramento.html'
        icon = 'list-ul'
        label = 'Central de Monitoramento'


class NoticiasListBlock(StructBlock):
    titulo = CharBlock(
        required=False,
        default="Últimas Notícias",
        help_text="Título exibido acima da lista de notícias"
    )

    noticias_index_page = PageChooserBlock(
        required=True,
        target_model='noticias.NoticiasIndexPages',
        help_text="Selecione a página de índice de notícias"
    )

    quantidade = IntegerBlock(
        required=False,
        default=6,
        min_value=1,
        label="Quantidade de notícias exibidas"
    )

    texto_link = CharBlock(
        required=False,
        default="Ver todas as notícias",
        label="Texto do link para todas as notícias"
    )

    mostrar_titulo = blocks.BooleanBlock(
        required=False,
        default=True,
        label="Mostrar título e linha abaixo?"
    )

    layout = blocks.ChoiceBlock(
        choices=[
            ('lista', 'Lista'),
            ('grid', 'Blocos'),
        ],
        default='lista',
        required=False,
        label="Layout das notícias"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        noticias_index_page = value.get('noticias_index_page')
        quantidade = value.get('quantidade') or 6
        texto_link = value.get('texto_link') or "Ver todas as notícias"

        noticias = []
        noticias_index_page_url = None

        if noticias_index_page:
            noticias = noticias_index_page.get_ultimas_noticias(quantidade=quantidade)
            noticias_index_page_url = noticias_index_page.url

        context.update({
            'titulo': value.get('titulo'),
            'noticias': noticias,
            'noticias_index_page_url': noticias_index_page_url,
            'texto_link': texto_link,
            'mostrar_titulo': value.get('mostrar_titulo', True),
            'layout': value.get('layout', 'lista'),
            'btn_classes': self.get_btn_classes(value),
        })

        return context
    
    def get_btn_classes(self, value):
        if getattr(settings, 'HABILITAR_SITE_INTRANET', False):
            return 'text-center'
        return 'text-center btn-ver-todos-bg-cinza'

    class Meta:
        template = 'blocks/list_noticias.html'
        icon = 'list-ul'
        label = 'Lista de Notícias'

class AvisosWidget(StructBlock):
    titulo = CharBlock(
        required=False,
        default="Destaques",
        help_text="Título exibido acima dos avisos"
    )
    mostrar_titulo = BooleanBlock(
        required=False,
        default=True,
        help_text="Marcar para exibir o título"
    )
    avisos_index_page = PageChooserBlock(
        required=True,
        target_model='avisos.AvisosIndexPage',
        help_text="Selecione a página de index de avisos."
    )
    quantidade = IntegerBlock(
        required=False,
        default=3,
        min_value=1,
        label="Quantidade de avisos em destaque"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        avisos_index_page = value.get('avisos_index_page')
        quantidade = value.get('quantidade') or 6
        avisos = []
        avisos_index_page_url = None

        if avisos_index_page:
            try:
                avisos = avisos_index_page.get_ultimos_avisos(quantidade=quantidade)
            except Exception:
                avisos = []
            avisos_index_page_url = avisos_index_page.url

        context['avisos'] = avisos
        context['avisos_index_page_url'] = avisos_index_page_url
        return context

    class Meta:
        template = "blocks/widget_avisos.html"
        icon = "star"
        label = "Destaques"

class AvisosListBlock(StructBlock):
    titulo = CharBlock(
        required=False,
        default="Quadro de Avisos",
        help_text="Título exibido acima dos avisos"
    )
    mostrar_titulo = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Marcar para exibir o título"
    )
    avisos_index_page = PageChooserBlock(
        required=True,
        target_model='avisos.AvisosIndexPage',
        help_text="Selecione a página de index de avisos."
    )
    quantidade = IntegerBlock(
        required=False,
        default=6,
        min_value=1,
        label="Quantidade de avisos exibidos"
    )
    texto_link = CharBlock(
        required=False,
        default="Ver todos os avisos",
        label="Texto do link para todos os avisos"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        avisos_index_page = value.get('avisos_index_page')
        quantidade = value.get('quantidade') or 6
        texto_link = value.get('texto_link') or "Ver todos os avisos"
        avisos = []
        avisos_index_page_url = None
        if avisos_index_page:
            try:
                avisos = avisos_index_page.get_ultimos_avisos(quantidade=quantidade)
            except Exception:
                avisos = []
            avisos_index_page_url = avisos_index_page.url
        context['avisos'] = avisos
        context['avisos_index_page_url'] = avisos_index_page_url
        context['texto_link'] = texto_link
        return context

    class Meta:
        template = "blocks/list_avisos.html"
        icon = "warning"
        label = "Avisos"

class LinkStructBlock(StructBlock):
    link_text = CharBlock(required=True, help_text="Texto")
    internal_page = PageChooserBlock(
        required=False, help_text="Link para uma página interna")
    external_url = URLBlock(
        required=False, help_text="Ou insira uma URL externa")

    def clean(self, value):
        cleaned_data = super().clean(value)
        if not cleaned_data.get('internal_page') and not cleaned_data.get('external_url'):
            raise ValidationError(
                'Você deve fornecer um link interno ou externo.')
        if cleaned_data.get('internal_page') and cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer apenas 1 link.')
        return cleaned_data

    def get_url(self, value):
        if value.get('internal_page'):
            return value['internal_page'].url
        return value.get('external_url')

    class Meta:
        icon = 'link'
        label = 'Link'


class LinkWithImageStructBlock(StructBlock):
    link_text = RichTextBlock(required=True, help_text="Texto")
    internal_page = PageChooserBlock(
        required=False, help_text="Link para uma página interna")
    external_url = URLBlock(
        required=False, help_text="Ou insira uma URL externa")
    image = ImageChooserBlock(
        required=False, help_text="Imagem opcional para o link")

    def clean(self, value):
        cleaned_data = super().clean(value)
        if not cleaned_data.get('internal_page') and not cleaned_data.get('external_url'):
            raise ValidationError(
                'Você deve fornecer um link interno ou externo.')
        if cleaned_data.get('internal_page') and cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer apenas 1 link.')
        return cleaned_data

    def get_url(self, value):
        if value.get('internal_page'):
            return value['internal_page'].url
        return value.get('external_url')

    class Meta:
        icon = 'link'
        label = 'Link'


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headers
    """

    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(
        choices=[
            ("", "Select a header size"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"
        preview_value = {"heading_text": "Healthy bread types", "size": "h2"}
        description = "Titulo com tamanho selecionável (H2, H3, H4)"


class CaptionedImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    @cached_property
    def preview_image(self):
        # Cache the image object for previews to avoid repeated queries
        return get_image_model().objects.last()

    def get_preview_value(self):
        return {
            **self.meta.preview_value,
            "image": self.preview_image,
            "caption": self.preview_image.description,
        }

    class Meta:
        icon = "image"
        template = "blocks/captioned_image_block.html"
        preview_value = {"attribution": "The Wagtail Bakery"}
        description = "Uma imagem com legenda e atribuição opcionais"


class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author
    """

    text = TextBlock()
    attribute_name = CharBlock(
        blank=True, required=False, label="e.g. Mary Berry")

    class Meta:
        icon = "openquote"
        template = "blocks/blockquote.html"
        preview_value = {
            "text": (
                "If you read a lot you're well read / "
                "If you eat a lot you're well bread."
            ),
            "attribute_name": "Willie Wagtail",
        }
        description = "Uma citação com atribuição opcional"


class IframeBlock(StructBlock):
    """
    Bloco para incorporar um iframe customizado.
    """
    url = URLBlock(required=True, label="URL do iframe")
    width = CharBlock(required=False, default="100%",
                      label="Largura", help_text="Exemplo: 100% ou 600")
    height = CharBlock(required=False, default="400",
                       label="Altura", help_text="Exemplo: 400")
    allowfullscreen = BooleanBlock(
        required=False, default=True, label="Permitir tela cheia")

    class Meta:
        icon = "site"
        label = "Iframe"
        template = "blocks/iframe_block.html"


class EspecificDocumentChooserBlock(DocumentChooserBlock):
    allowed_extensions = ['.pdf', '.txt',
                          '.doc', '.docx', '.ods', '.xls', '.xlsx']
    allowed_mimetypes = [
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]

    def __init__(self, *args, allowed_extensions=None, allowed_mimetypes=None, **kwargs):
        super().__init__(*args, **kwargs)
        if allowed_extensions is not None:
            self.allowed_extensions = allowed_extensions
        if allowed_mimetypes is not None:
            self.allowed_mimetypes = allowed_mimetypes

    def clean(self, value):
        value = super().clean(value)
        if value and value.file:
            # Validação por extensão
            if not any(value.file.name.lower().endswith(ext) for ext in self.allowed_extensions):
                raise ValidationError(
                    f"Apenas arquivos permitidos: {', '.join(self.allowed_extensions).upper()}."
                )
            # Validação por mimetype usando libmagic
            mime = magic.Magic(mime=True)
            mimetype = mime.from_buffer(value.file.read(2048))
            value.file.seek(0)  # volta o ponteiro do arquivo
            if mimetype not in self.allowed_mimetypes:
                raise ValidationError(
                    f"Tipo de arquivo não permitido ({mimetype}). Permitidos: {', '.join(self.allowed_extensions).upper()}."
                )
        return value


class CardLinhaDoTempoBlock(StructBlock):
    imagem = ImageChooserBlock(required=True, label="Imagem")
    texto_alternativo = CharBlock(
        required=False, label="Texto alternativo da imagem")
    titulo = CharBlock(required=False, label="Título")
    descricao = TextBlock(required=False, label="Descrição")
    internal_page = PageChooserBlock(
        required=False,
        target_model='linhasdotempo.CardLinhaDoTempoPage',
        label="Página interna de evento da linha do tempo.",
        help_text="Se as informações da descrição ultrapassarem o limite de exibição estabelecido, \
        você poderá criar uma nova página com as informações completas, a qual estará disponível\
        no card através do link 'Ver mais' ou clicando no card."
    )
    external_url = URLBlock(
        required=False,
        label="URL externa com informações adicionais de evento da linha do tempo.",
        help_text="Ou adicionar uma fonte externa, a qual também ficará disponível\
        no card através do link 'Ver mais' ou clicando no card."
    )
    # data = DateBlock(required=True, label="Data")

    def clean(self, value):
        cleaned_data = super().clean(value)
        if not cleaned_data.get('internal_page') and not cleaned_data.get('external_url'):
            raise ValidationError(
                'Você deve fornecer um link interno ou externo.')
        if cleaned_data.get('internal_page') and cleaned_data.get('external_url'):
            raise ValidationError('Você deve fornecer apenas 1 link.')
        return cleaned_data

    def get_url(self, value):
        if value.get('internal_page'):
            return value['internal_page'].url
        return value.get('external_url')

    class Meta:
        icon = 'title'
        label = 'Card da Linha do Tempo'
        template = 'blocks/card_linha_do_tempo.html'
        form_attrs = {
            'data-controller': 'char-count',
            'data-char-count-fields-value': 'titulo:50,descricao:220',
        }


# StreamBlocks


class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    
    """
    '''
    titulo_bloco = TituloBlock(
        label="Título",
        description="Um título simples com opção de cor de fundo."
    )
    '''
    paragraph_block = RichTextBlock(
        icon="pilcrow",
        label="Texto de Parágrafo",
        template="blocks/paragraph_block.html",
        preview_value=(
            """
            <h2>Our bread pledge</h2>
            <p>As a bakery, <b>breads</b> have <i>always</i> been in our hearts.
            <a href="https://en.wikipedia.org/wiki/Staple_food">Staple foods</a>
            are essential for society, and – bread is the tastiest of all.
            We love to transform batters and doughs into baked goods with a firm
            dry crust and fluffy center.</p>
            """
        ),
        description="Um parágrafo de texto rico",
    )
    image_block = CaptionedImageBlock(
        label="Bloco de Imagem com Legenda",
    )
    '''
    block_quote = BlockQuote(
        label="Bloco de Citação",
        description="Uma citação com atribuição opcional",
    )
    '''
    video_block = VideoBlock(
        label="Bloco de Vídeo",
    )
    '''
    iframe_block = IframeBlock(
        label="Bloco de Iframe",
        help_text="Adicione uma URL https://example.com",
        icon="site",
        template="blocks/iframe_block.html",
        # preview_template="blocks/preview/static_iframe_block.html",
        # preview_value="https://example.com", 
        description="Um iframe incorporado",
    )
    '''
    table_block = TableBlock(
        label="Bloco de Tabela",
        help_text="Insira os dados da tabela",
        icon="table",
        template="blocks/table.html",
        # preview_template="blocks/preview/static_table_block.html",
        description="Uma tabela de dados",
    )


class LinhaDoTempoBlock(StructBlock):
    titulo = CharBlock(required=True, label="Título")
    cards = ListBlock(CardLinhaDoTempoBlock(), min_num=1,
                      max_num=12, icon='form', label="Card")

    class Meta:
        icon = 'title'
        label = 'Linha do Tempo'
        template = 'blocks/linha_do_tempo.html'


class SolucaoItemBlock(StructBlock):
    imagem = ImageChooserBlock(required=True, label="Imagem do Solução")
    link = URLBlock(required=True, label="URL do Solução")
    texto_alternativo = CharBlock(
        required=False,
        label="Texto alternativo",
        help_text="Descrição da imagem para acessibilidade (alt text)"
    )

    class Meta:
        icon = 'image'
        label = "Item de Solução"
        template = 'blocks/item_solucao.html'


class CarrosselSolucoesBlock(StructBlock):
    titulo = CharBlock(required=False, default="Soluções")
    solucoes = ListBlock(
        SolucaoItemBlock(),
        label="Soluções",
        help_text="Adicione as soluções para o carrossel"
    )

    class Meta:
        icon = 'image'
        label = "Carrossel de Soluções"
        template = 'blocks/carrossel_solucoes.html'


class GridImageItemBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100,
                       label="Título da Imagem")
    link = URLBlock(required=True, label="Link da Imagem")
    imagem = ImageChooserBlock(required=True, label="Imagem da Imagem")

    class Meta:
        icon = 'imagem'
        label = 'Imagem do Grid'


class GridImagensBlock(StructBlock):
    titulo = CharBlock(
        required=True, label="Titulo do bloco Ex.: Programas, Orgãos Vinculados", default="Programas")
    link_ver_todos = URLBlock(
        required=False, label="Link do botão 'Ver todos'")
    grid_type = ChoiceBlock(choices=GRID_IMAGENS_TYPES,
                            default=GRID_IMAGENS_DEFAULT_TYPE,
                            required=True, label="Tipo de Grid")
    itens = ListBlock(GridImageItemBlock, min_num=1, max_num=12)

    def get_column_classes(self, grid_type):
        """
        Retorna as classes de coluna Bootstrap baseadas no tipo de grid.
        """
        return GRID_IMAGENS_CLASSES.get(grid_type, GRID_IMAGENS_CLASSES[GRID_IMAGENS_DEFAULT_TYPE])

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        grid_type = value.get('grid_type', GRID_IMAGENS_DEFAULT_TYPE)
        context['column_classes'] = self.get_column_classes(grid_type)
        return context

    class Meta:
        icon = 'list-ul'
        label = "Grid de Imagens"
        template = 'blocks/grid_imagens.html'

class BaseStreamCorpoTecnicoBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """

    paragraph_block = RichTextBlock(
        icon="pilcrow",
        template="blocks/paragraph_block.html",
        preview_value=(
            """
            <h2>Our bread pledge</h2>
            <p>As a bakery, <b>breads</b> have <i>always</i> been in our hearts.
            <a href="https://en.wikipedia.org/wiki/Staple_food">Staple foods</a>
            are essential for society, and – bread is the tastiest of all.
            We love to transform batters and doughs into baked goods with a firm
            dry crust and fluffy center.</p>
            """
        ),
        description="A rich text paragraph",
    )
    
class ItemListaInformativaBlock(StructBlock):
    texto = CharBlock(required=False, help_text="Use para um item de texto simples (um por linha).")
    titulo_link = CharBlock(required=False, help_text="Texto que será exibido para o link.")
    url_link = URLBlock(required=False, help_text="URL para onde o link aponta.")
    arquivo = DocumentChooserBlock(required=False, help_text="Selecione um arquivo para download (máx 10MB).", validators=[validate_file_size])

    def clean(self, value):
        cleaned_data = super().clean(value)
        is_texto = bool(cleaned_data.get('texto'))
        is_link = bool(cleaned_data.get('titulo_link') or cleaned_data.get('url_link'))
        is_arquivo = bool(cleaned_data.get('arquivo'))
        tipos_preenchidos = sum([is_texto, is_link, is_arquivo])
        if tipos_preenchidos > 1:
            raise ValidationError("Escolha apenas um tipo de item: texto, link ou arquivo.")
        if tipos_preenchidos == 0:
            raise ValidationError("Você deve preencher um dos tipos de item: texto, link ou arquivo.")
        if is_link and not (cleaned_data.get('titulo_link') and cleaned_data.get('url_link')):
            raise ValidationError("Para um link, tanto o 'Título do link' quanto a 'URL' são obrigatórios.")
        return cleaned_data

    class Meta:
        label = "Item da Lista"
        icon = "dot-circle"

class TextoSimplesBlock(StructBlock):
    texto = RichTextBlock(required=True, label="Texto", features=['bold', 'italic', 'ol', 'ul', 'link', 'document-link'])

    class Meta:
        label = "Texto Simples"
        icon = "pilcrow"
        template = "blocks/texto_simples_block.html"

class LinkBlock(StructBlock):
    titulo_link = CharBlock(required=True, label="Texto do Link")
    url_link = URLBlock(required=True, label="URL do Link")

    class Meta:
        label = "Link"
        icon = "link"
        template = "blocks/link_block.html"

class ArquivoDownloadBlock(StructBlock):
    titulo_arquivo = CharBlock(required=True, label="Texto de exibição para o arquivo")
    arquivo = DocumentChooserBlock(required=True, label="Arquivo para Download")

    class Meta:
        label = "Arquivo para Download"
        icon = "doc-full-inverse"
        template = "blocks/arquivo_download_block.html"

class ConteudoAcordeonStreamBlock(StreamBlock):
    texto = TextoSimplesBlock()
    link = LinkBlock()
    arquivo = ArquivoDownloadBlock()

    class Meta:
        label = "Conteúdo da Seção"

class AcordeonItemBlock(StructBlock):
    titulo = CharBlock(required=True, label="Título da Seção")
    conteudo = ConteudoAcordeonStreamBlock(required=False, label="Conteúdo da Seção")
    class Meta:
        label = "Item do Acordeão"
        icon = "collapse-down"


class AcordeonBlock(StructBlock):
    titulo_geral = CharBlock(required=False, label="Título Geral do Bloco de Acordeão")
    secoes = ListBlock(
        AcordeonItemBlock(),
        label="Seções do Acordeão",
        help_text="Adicione uma ou mais seções expansíveis."
    )
    TEMAS = [
        ('branco', 'Branco (Padrão)'),
        ('azul', 'Azul com cinza'),
    ]
    tema = ChoiceBlock(
        choices=TEMAS,
        default='branco',
        required=False,
        label="Tema de Cores do Acordeão",
        help_text="A cor escolhida será aplicada a todas as seções do acordeão."
    )

    class Meta:
        label = "Acordeão"
        icon = "collapse-down"
        template = "blocks/bloco_informativo.html"
class CustomFormBlock(StructBlock):
    titulo_geral = CharBlock(default="Formulário", label="Título Principal do Formulário", help_text="Título que será exibido acima do formulário.")
    descricao = RichTextBlock(required=False, label="Descrição/Introdução")
    campos_customizados = StreamBlock([
        ('texto_simples', SingleLineFieldBlock()),
        ('texto_longo', MultiLineFieldBlock()),
        ('email', EmailFieldBlock()),
        ('numero', NumberFieldBlock()),
        ('arquivo', FileFieldBlock()),
    ], label="Campos Customizados", required=False)
    texto_botao = CharBlock(default="Enviar", label="Texto do Botão de Envio")
    captcha_habilitado = BooleanBlock(required=False, default=False, label="Habilitar reCAPTCHA")

    def get_context(self, value, parent_context=None):
        from .forms import CustomForm
        context = super().get_context(value, parent_context)
        request = context.get('request')
        initial_data = {}
        if request and request.user.is_authenticated:
            initial_data['nome_completo'] = request.user.get_full_name() or request.user.username
        show_recaptcha = bool(value.get('captcha_habilitado'))

        recaptcha_site_key = None
        recaptcha_secret_key = None
        try:
            from core.models import SiteSettings
            site_settings = SiteSettings.for_site(request.site) if request and hasattr(request, 'site') else SiteSettings.objects.first()
            if site_settings:
                recaptcha_site_key = site_settings.get_captcha_site_key()
                recaptcha_secret_key = site_settings.get_captcha_secret()
                if not (recaptcha_site_key and recaptcha_secret_key):
                    show_recaptcha = False
        except Exception:
            show_recaptcha = False

        form = CustomForm(
            fields_config=value.get('campos_customizados'),
            initial=initial_data,
            request=request,
            show_recaptcha=show_recaptcha,
            recaptcha_secret_key=recaptcha_secret_key
        )
        # Se um formulário com erros foi passado pelo `serve`, use-o.
        if request and hasattr(request, '_form_errors') and getattr(request, '_form_errors') is not None:
            form = getattr(request, '_form_errors')

        context['form'] = form
        context['show_recaptcha'] = show_recaptcha
        context['recaptcha_site_key'] = recaptcha_site_key
        return context

    class Meta:
        label = "Formulário Customizado"
        icon = "form"
        template = "blocks/formulario.html"


class ArquivoSubmetido(models.Model):
    submissao = models.ForeignKey('FormularioSubmissao', on_delete=models.CASCADE, related_name='arquivos_submetidos')
    nome_campo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='formularios_submetidos/')

    def __str__(self):
        return f"Arquivo do campo '{self.nome_campo}' para a submissão {self.submissao.id}"

class FormularioSubmissao(models.Model):
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    titulo = models.CharField(max_length=255, verbose_name="Título")
    dados_adicionais = models.JSONField(verbose_name="Dados Adicionais", help_text="Campos customizados do formulário.")
    pagina = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Página de origem"
    )
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de envio")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário da Intranet?"
    )

    def dados_adicionais_formatados(self):
        if not self.dados_adicionais:
            return "Nenhum dado adicional."
        return format_html_join(
            '', '<h4>{}:</h4> {}',
            ((key, value) for key, value in self.dados_adicionais.items())
        )
    dados_adicionais_formatados.short_description = "Dados Adicionais"
    
    def arquivos_para_download(self):
        try:
            form_block_value = next(block.value for block in self.pagina.specific.body if isinstance(block.block, CustomFormBlock))
            field_map = {f"custom_field_{i}_{block.block_type}": block.value.get('label') for i, block in enumerate(form_block_value.get('campos_customizados', []))}
        except (StopIteration, AttributeError):
            field_map = {}

        return format_html_join(
            ' / ',
            '<a href="{}" target="_blank">{}</a>',
            ((arquivo.arquivo.url, field_map.get(arquivo.nome_campo, arquivo.nome_campo)) for arquivo in self.arquivos_submetidos.all())
        )

    arquivos_para_download.short_description = "Arquivos Anexados"


    def __str__(self):
        return f"Envio de {self.nome_completo} em {self.pagina.title if self.pagina else 'N/A'}"

    class Meta:
        verbose_name = "Envio do Formulário"
        verbose_name_plural = "Envios dos Formulários"
        ordering = ['-data_envio']
