import os
import magic

from wagtail.admin.panels import PanelPlaceholder
from django.forms import TextInput, Textarea

# Limite default de caracteres para o campo de título
TITLE_CHAR_LIMIT = 255

# Limite default de caracteres para o campos no qual o widget for aplicado
INPUT_CHAR_LIMIT = 255

def get_file_type(file_obj):
    """
    Retorna uma string com o tipo do arquivo, priorizando o mimetype sobre a extensão.
    Exemplo de retorno: 'pdf', 'docx', 'xls', 'txt', etc.
    """
    # Tenta pegar a extensão pelo nome
    ext = ''
    if hasattr(file_obj, 'name'):
        ext = os.path.splitext(file_obj.name)[1].lower().replace('.', '')
    elif isinstance(file_obj, str):
        ext = os.path.splitext(file_obj)[1].lower().replace('.', '')

    # Tenta pegar o mimetype usando libmagic
    mimetype = None
    try:
        if hasattr(file_obj, 'file'):
            mime = magic.Magic(mime=True)
            mimetype = mime.from_buffer(file_obj.file.read(2048))
            file_obj.file.seek(0)
        elif hasattr(file_obj, 'read'):
            mime = magic.Magic(mime=True)
            mimetype = mime.from_buffer(file_obj.read(2048))
            file_obj.seek(0)
        elif isinstance(file_obj, str) and os.path.exists(file_obj):
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(file_obj)
    except Exception:
        mimetype = None

    # Mapeamento simples de mimetype para tipo
    mimetype_map = {
        'application/pdf': 'pdf',
        'text/plain': 'txt',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/vnd.oasis.opendocument.spreadsheet': 'ods',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'application/zip': 'zip',
        'application/x-rar-compressed': 'rar',
        'text/csv': 'csv',
    }

    mimetype_type = mimetype_map.get(mimetype, '')

    # Se mimetype e extensão diferem, dê preferência ao mimetype se identificado
    if mimetype_type:
        return mimetype_type
    if ext:
        return ext
    return ''


def get_fontawesome_file_icon(file_type):
    """
    Retorna a classe do ícone FontAwesome de acordo com o tipo do arquivo.
    Exemplo de retorno: 'fa-file-pdf', 'fa-file-word', etc.
    """
    mapping = {
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'xls': 'fa-file-excel',
        'xlsx': 'fa-file-excel',
        'ods': 'fa-file-excel',
        'txt': 'fa-file-lines',
        'csv': 'fa-file-csv',
        'zip': 'fa-file-zipper',
        'rar': 'fa-file-zipper',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
    }
    return mapping.get(file_type, '')


def get_page_title_with_counter(char_limit=TITLE_CHAR_LIMIT):
    """
    Retorna um painel com o campo de título com contador de caracteres.
    Caso não seja definido um valor para o limite de caracteres, será
    utilizado o valor padrão de 255.
    """
    return [
        PanelPlaceholder("wagtail.admin.panels.TitleFieldPanel", ["title"], {
            'widget': get_widget_input_with_counter(
                char_limit=char_limit,
                InputField=TextInput
            ),
        }),
    ]


def get_widget_input_with_counter(
    char_limit: int = INPUT_CHAR_LIMIT,
    InputField: TextInput | Textarea = Textarea
):
    """
    Retorna um campo de entrada <<input> | <textarea>> com contador de caracteres.
    Caso não seja definido um valor para o limite de caracteres, será
    utilizado o valor padrão de 255.
    O tipo de campo pode ser TextInput ou Textarea, sendo Textarea a opção padrão.
    """
    return InputField(attrs={
        'data-controller': 'char-count',
        'data-char-count-max-value': char_limit,
    })


def get_parent_field(page_instance, field_name):
    """
    Retorna o valor de um campo específico da página pai.
    Se a página pai não existir ou não tiver o campo, retorna uma string vazia.
    """
    parent = page_instance.get_parent()
    if parent:
        parent_specific = parent.specific
        return getattr(parent_specific, field_name, "")
    return ""
