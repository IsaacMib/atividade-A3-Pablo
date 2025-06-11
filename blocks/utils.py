# utils.py

ICONES_REDES = [
    ('fa-brands fa-facebook', 'Facebook'),
    ('fa-brands fa-instagram', 'Instagram'),
    ('fa-brands fa-youtube', 'YouTube'),
    ('fa-brands fa-spotify', 'Spotify'),
    ('fa-brands fa-twitter', 'Twitter'),
    ('fa-brands fa-tiktok', 'TikTok'),
    ('fa-brands fa-linkedin', 'LinkedIn'),
    ('fa-brands fa-whatsapp', 'WhatsApp'),
    ('fa-brands fa-telegram', 'Telegram'),
]
ICONES_ACESSO_RAPIDO = [
    ('fas fa-comments', 'Ouvidoria'),
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

IDS_METABASE_CARDS = [
    (2650, 'Frota de Veículos'),
    (3447, 'Condutores residentes na Paraíba'),
    (3755, 'Infrações cometidas no ano atual'),
    (3756, "CNH's pelo PHS"),
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

