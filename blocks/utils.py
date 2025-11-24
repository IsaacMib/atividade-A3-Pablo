# utils.py
from django.core.exceptions import ValidationError

# Ícones de Redes Sociais
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

# Cores de fundo para títulos
CLASS_TITULO_BG_COLOR_BLOCK = [
    ('titulo-bg-default', 'Background Padrão'),
    ('titulo-bg-azul', 'Background Tipo 1'),
    ('titulo-bg-cinza', 'Background Tipo 2')
]

# Tipos de Grid de Imagens
GRID_IMAGENS_TYPES = [
    ('grid-imagens-2', 'Grid com 2 imagens por linha'),
    ('grid-imagens-3', 'Grid com 3 imagens por linha'),
    ('grid-imagens-4', 'Grid com 4 imagens por linha'),
    ('grid-imagens-6', 'Grid com 6 imagens por linha'),
]

GRID_IMAGENS_DEFAULT_TYPE = 'grid-imagens-3'

GRID_IMAGENS_CLASSES = {
    'grid-imagens-2': 'col-12 col-md-6 d-flex justify-content-center',
    'grid-imagens-3': 'col-12 col-md-4 d-flex justify-content-center',
    'grid-imagens-4': 'col-6 col-md-3 d-flex justify-content-center',
    'grid-imagens-6': 'col-6 col-md-2 d-flex justify-content-center',
}

# Validação de tamanho de arquivo
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
