# utils.py

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
    (2650, 'Total de Unicades Escolares(UE)'),
    (3447, 'Total de Matrículas na Educação Básica'),
    (3755, 'Total de Turmas na Educação Básica'),
    (3756, "Total de Vagas na Educação Básica"),
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

COLOR_TITULO_BG_COLOR_BLOCK = [
    ('#305A9C' , 'titulo-bg-default'),
    ('#305A9C' , 'titulo-bg-cinza'),
    ('#FFFFFF' , 'titulo-bg-azul'),
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

def get_color_by_class_titulo_bg(class_name):
    """
    Retorna a cor correspondente ao class_name presente em CLASS_TITULO_BG_COLOR_BLOCK,
    buscando o valor correspondente em COLOR_TITULO_BG_COLOR_BLOCK.
    Se não encontrar, retorna #305A9C.
    """
    # Busca o nome da cor correspondente ao class_name
    for color, class_option in COLOR_TITULO_BG_COLOR_BLOCK:
        if class_option == class_name:
            return color
    return '#305A9C'

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
