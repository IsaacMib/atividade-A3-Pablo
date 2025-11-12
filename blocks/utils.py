# utils.py
from django.core.exceptions import ValidationError

ICONES_REDES_GERAL = [
    ('fa-brands fa-facebook', 'Facebook'),
    ('fa-brands fa-instagram', 'Instagram'),
    ('fa-brands fa-youtube', 'YouTube'),
    ('fa-brands fa-spotify', 'Spotify'),
    ('fa-brands fa-square-x-twitter', 'X'),
    ('fa-brands fa-tiktok', 'TikTok'),
    ('fa-brands fa-linkedin', 'LinkedIn'),
    ('fa-brands fa-whatsapp', 'WhatsApp'),
    ('fa-brands fa-telegram', 'Telegram'),
]

ICONES_REDES = sorted(ICONES_REDES_GERAL, key=lambda x: x[1])

ICONES_ACESSO_RAPIDO_GERAL = [
    ('fas fa-headset', 'Atendimentos'),
    ('fas fa-video', 'PB Meet'),
    ('fas fa-envelope', 'WebMail'),
    ('fas fa-file-contract', 'Contracheque'),
    ('fas fa-globe', 'PB.GOV.BR'),
    ('fas fa-building', 'Lotações'),
    ('fas fa-server', 'CABSI'),
    ('fas fa-chart-bar', 'Transparência'),
    ('fas fa-lock', 'LGPD'),
    ('fas fa-file-alt', 'PBDoc'),
    ('fas fa-calculator', 'SIAF'),
    ('fas fa-hand-holding-usd', 'PBConsig'),
    ('fas fa-gavel', 'Licitações'),
    ('fas fa-database', 'Sistemas Internos'),
    ('fas fa-book', 'Manuais e Documentos'),
    ('fas fa-cloud-upload-alt', 'Upload de Arquivos'),
    ('fas fa-network-wired', 'Infraestrutura'),
    ('fas fa-calendar-alt', 'Agenda Corporativa'),
    ('fas fa-mobile-alt', 'Aplicativos Móveis'),
    ('fas fa-shield-alt', 'Segurança da Informação'),
    ('fas fa-tools', 'Ferramentas Administrativas'),
]

ICONES_ACESSO_RAPIDO_DETRAN = [
    ('fas fa-file-invoice', 'Boleto Licenciamento'),
    ('fas fa-money-bill-wave', 'IPVA'),
    ('fas fa-car', '1º Emplacamento on-line (0km)'),
    
    ('fas fa-id-card', 'ATPVe'),
    ('fas fa-receipt', 'Taxas de Serviços'),
    ('fas fa-question-circle', 'Perguntas Frequentes'),
    ('fas fa-search', 'Consultar Proc. Veículo'),
    
    ('fas fa-file-alt', 'Portaria/Instruções Normativas'),
    ('fas fa-clipboard-check', 'Menu de Exames'),
    ('fas fa-phone-alt', 'Telefones Úteis'),
    ('fas fa-folder-open', 'Consultar Processo SGP'),

    # Ícones adicionais
    ('fas fa-calendar-check', 'Agendamento de Serviços'),
    ('fas fa-id-badge', 'CNH Digital'),
    ('fas fa-exclamation-triangle', 'Segurança no Trânsito'),
    ('fas fa-car-crash', 'Consulta de Multas'),
    ('fas fa-map-marked-alt', 'Localização de Postos'),
    ('fas fa-tools', 'Serviços Gerais'),
    ('fas fa-user-shield', 'Área do Condutor'),
]


ICONES_ACESSO_RAPIDO_EDUCACAO = [
    ('fas fa-file-contract', 'Licitações, contratos'),
    ('fas fa-file-alt', 'Editais'),
    ('fas fa-search', 'Consultas'),
    ('fas fa-project-diagram', 'Programas'),
    
    ('fas fa-school', 'Escolas'),
    ('fas fa-building', 'Gerências'),
    ('fas fa-concierge-bell', 'Serviços'),
    ('fas fa-user-tie', 'Portal do Servidor'),
    
    ('fas fa-comments', 'Ouvidoria'),
    ('fas fa-phone-alt', 'Contatos'),
    ('fas fa-ellipsis-h', 'Outros'),
]

ICONES_ACESSO_RAPIDO = sorted(
    ICONES_ACESSO_RAPIDO_GERAL + ICONES_ACESSO_RAPIDO_EDUCACAO + ICONES_ACESSO_RAPIDO_DETRAN,
    key=lambda x: x[1]
)

IDS_METABASE_CARDS_DETRAN = [
    (2650, 'Frota de Veículos'),
    (3447, 'Condutores residentes na Paraíba'),
    (3755, 'Infrações cometidas no ano atual'),
    (3756, "CNH's pelo PHS"),
]


IDS_METABASE_CARDS_EDUCACAO = [
    (2651, 'Total de Unicades Escolares(UE)'),
    (3448, 'Total de Matrículas na Educação Básica'),
    (3757, 'Total de Turmas na Educação Básica'),
    (3758, "Total de Vagas na Educação Básica"),
]

IDS_METABASE_CARDS = sorted(
    IDS_METABASE_CARDS_EDUCACAO + IDS_METABASE_CARDS_DETRAN,
    key=lambda x: x[1]
)

CLASS_TITULO_BG_COLOR_BLOCK = [
    ('titulo-bg-default' , 'Background Padrão'),
    ('titulo-bg-azul' , 'Background Tipo 1'),
    ('titulo-bg-cinza' , 'Background Tipo 2')
]

def get_metabase_card_text_by_id(card_id):
    """
    Retorna o texto correspondente ao id informado no array IDS_METABASE_CARDS.
    Se não encontrar, retorna uma string vazia.
    """
    for id_opcao, texto in IDS_METABASE_CARDS:
        if str(id_opcao) == str(card_id):
            return texto
    return ""

GRID_IMAGENS_TYPES = [
    ('grid-imagens-2', 'Grid com 2 imagens por linha'),
    ('grid-imagens-3', 'Grid com 3 imagens por linha'),
    ('grid-imagens-4', 'Grid com 4 imagens por linha'),
    ('grid-imagens-6', 'Grid com 6 imagens por linha'),
]

GRID_IMAGENS_DEFAULT_TYPE = 'grid-imagens-3'

GRID_IMAGENS_CLASSES = {
    'grid-imagens-2': 'col-12 col-md-6 d-flex justify-content-center',      # 2 colunas por linha
    'grid-imagens-3': 'col-12 col-md-4 d-flex justify-content-center',       # 3 colunas por linha
    'grid-imagens-4': 'col-6 col-md-3 d-flex justify-content-center',       # 4 colunas por linha
    'grid-imagens-6': 'col-6 col-md-2 d-flex justify-content-center',       # 6 colunas por linha
}

def validate_file_size(value):
    file_obj = getattr(value, 'file', value)
    if file_obj and hasattr(file_obj, 'size') and file_obj.size > 10 * 1024 * 1024:
        raise ValidationError("O tamanho do arquivo não pode exceder 10MB.")

# Configurações de Banner
BANNER_MODES = [
    ('fill', 'Preencher (fill) - Recorta para preencher exatamente'),
    ('max', 'Máximo (max) - Mantém proporção até tamanho máximo'),
    ('min', 'Mínimo (min) - Garante tamanho mínimo sem estourar'),
    ('original', 'Original - Sem redimensionamento'),
]

BANNER_SIZES = [
    ('original', '🖼️ Original (sem redimensionar)'),
    
    # Ícones e miniaturas
    ('16x16', '🔹 Mini ícone (16x16)'),
    ('32x32', '🔹 Ícone pequeno (32x32)'),
    ('64x64', '🔹 Ícone médio (64x64)'),
    ('128x128', '🔹 Ícone grande (128x128)'),
    
    # Miniaturas quadradas
    ('200x200', '🟦 Miniatura quadrada (200x200)'),
    ('230x230', '🟦 Miniatura média (230x230)'),
    ('273x273', '🟦 Miniatura grande (273x273)'),
    ('370x370', '🟦 Thumbnail padrão (370x370)'),
    ('400x400', '🟦 Quadrado médio (400x400)'),
    ('468x468', '🟦 Quadrado grande (468x468)'),
    ('565x565', '🟦 Quadrado XL (565x565)'),
    ('663x663', '🟦 Quadrado XXL (663x663)'),
    ('760x760', '🟦 Quadrado 4:4 (760x760)'),
    ('1150x1150', '🟦 Capa quadrada (1150x1150)'),
    
    # Horizontais e widescreen
    ('128x85', '📺 Mini horizontal (128x85)'),
    ('238x133', '📺 Banner pequeno (238x133)'),
    ('750x420', '📺 Banner médio (750x420)'),
    ('768x420', '📺 Banner padrão (768x420)'),
    ('1150x650', '📺 Capa Desktop (1150x650)'),
    ('1200x450', '📺 Capa Wide (1200x450)'),
    ('1366x768', '📺 Full HD 16:9 (1366x768)'),
    ('1920x1080', '📺 HD 16:9 (1920x1080)'),
    ('2560x1440', '📺 QHD 16:9 (2560x1440)'),
    ('3840x2160', '📺 4K Ultra HD (3840x2160)'),
    
    # Verticais e retratos
    ('480x640', '📱 Retrato pequeno (480x640)'),
    ('720x1080', '📱 Retrato padrão (720x1080)'),
    ('1080x1350', '📱 Retrato social (1080x1350)'),
    ('1080x1920', '📱 Story / Vertical (1080x1920)'),
]
