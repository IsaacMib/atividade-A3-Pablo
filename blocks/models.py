from blocks.utils import (
    ICONES_REDES,
    ICONES_ACESSO_RAPIDO,
    IDS_METABASE_CARDS,
    CLASS_TITULO_BG_COLOR_BLOCK,
    GRID_IMAGENS_TYPES,
    GRID_IMAGENS_CLASSES,
    GRID_IMAGENS_DEFAULT_TYPE,
    get_metabase_card_text_by_id
)

import requests
from django.core.cache import cache
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
    BooleanBlock
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.embeds.blocks import EmbedBlock
from django.utils.functional import cached_property
from wagtail.images import get_image_model
from django.conf import settings
import uuid

import magic

from django.core.exceptions import ValidationError

mappingIconsServicos = {
    'HIBRIDO': 'icon: link; ratio: 0.75',
    'PRESENCIAL': 'icon: user; ratio: 0.75',
    'ONLINE': 'icon: desktop; ratio: 0.75',
    'PRESENCIAL_AGENDAMENTO': 'icon: calendar; ratio: 0.75',
}


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
        icon = 'list-ul'
        label = "Bloco de Acessos Rápidos"
        template = 'blocks/list_acesso_rapido.html'


class BannerComLinkBlock(StructBlock):
    imagem = ImageChooserBlock(required=True, label="Imagem do Banner")
    link = URLBlock(required=True, label="URL do Banner")
    alt_texto = CharBlock(required=False, label="Texto alternativo",
                          help_text="Descrição da imagem (alt)")

    class Meta:
        icon = 'image'
        label = "Banner com Link"
        template = 'blocks/banner.html'


class VideoBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100)
    srcIframe = URLBlock(required=True, label="URL do vídeo (iframe YouTube)")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        url = value.get('srcIframe')

        # Transforma links padrão do YouTube em formato embed
        if 'watch?v=' in url:
            url = url.replace('watch?v=', 'embed/')
        elif 'youtu.be/' in url:
            url = url.replace('youtu.be/', 'www.youtube.com/embed/')

        context['titulo'] = value.get('titulo')
        context['src'] = url
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


_CACHE_TIMEOUT = 600  # 10 minutos em segundos


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
        help_text="Título que aparecerá acima da lista de notícias"
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

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        noticias_index_page = value.get('noticias_index_page')
        quantidade = value.get('quantidade') or 6
        texto_link = value.get('texto_link') or "Ver todas as notícias"
        noticias = []
        noticias_index_page_url = None
        if noticias_index_page:
            noticias = noticias_index_page.get_ultimas_noticias(
                quantidade=quantidade)
            noticias_index_page_url = noticias_index_page.url
        context['noticias'] = noticias
        context['noticias_index_page_url'] = noticias_index_page_url
        context['texto_link'] = texto_link
        return context

    class Meta:
        template = 'blocks/list_noticias.html'
        icon = 'list-ul'
        label = 'Lista de Notícias'


class AvisosListBlock(StructBlock):
    titulo = CharBlock(
        required=False,
        default="Últimos Avisos",
        help_text="Título que aparecerá acima da lista de avisos"
    )
    avisos_index_page = PageChooserBlock(
        required=True,
        target_model='avisos.AvisosIndexPage',
        help_text="Selecione a página de index de avisos"
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
            avisos = avisos_index_page.get_ultimos_avisos(
                quantidade=quantidade)
            avisos_index_page_url = avisos_index_page.url
        context['avisos'] = avisos
        context['avisos_index_page_url'] = avisos_index_page_url
        context['texto_link'] = texto_link
        return context

    class Meta:
        template = 'blocks/list_avisos.html'
        icon = 'warning'
        label = 'Lista de Avisos'


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
        description = "An image with optional caption and attribution"


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
        description = "A quote with an optional attribution"


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

# StreamBlocks


class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """

    heading_block = HeadingBlock()
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
    image_block = CaptionedImageBlock()
    block_quote = BlockQuote()
    embed_block = EmbedBlock(
        help_text="Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
        icon="media",
        template="blocks/embed_block.html",
        preview_template="blocks/preview/static_embed_block.html",
        preview_value="https://www.youtube.com/watch?v=mwrGSfiB1Mg",
        description="An embedded video or other media",
    )
    iframe_block = IframeBlock(
        help_text="Insert an iframe URL e.g https://example.com",
        icon="site",
        template="blocks/iframe_block.html",
        # preview_template="blocks/preview/static_iframe_block.html",
        # preview_value="https://example.com",
        description="An embedded iframe",
    )
    table_block = TableBlock(
        help_text="Insira os dados da tabela",
        icon="table",
        # template="blocks/table_block.html",
        # preview_template="blocks/preview/static_table_block.html",
        description="Uma tabela de dados",
    )


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


class ProgramaItemBlock(StructBlock):
    titulo = CharBlock(required=True, max_length=100,
                       label="Título do Programa")
    link = URLBlock(required=True, label="Link do Programa")
    imagem = ImageChooserBlock(required=True, label="Imagem do Programa")

    class Meta:
        icon = 'imagem'
        label = 'Item do Programa'


class GridImagensBlock(StructBlock):
    titulo = CharBlock(required=True, label="Titulo do bloco Ex.: Programas, Soluções", default="Programas")
    link_ver_todos = URLBlock(
        required=False, label="Link do botão 'Ver todos'")
    grid_type = ChoiceBlock(choices=GRID_IMAGENS_TYPES,
                             default=GRID_IMAGENS_DEFAULT_TYPE,
                             required=True, label="Tipo de Grid")
    itens = ListBlock(ProgramaItemBlock, min_num=1, max_num=12)
    
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
