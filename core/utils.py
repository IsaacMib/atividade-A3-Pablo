import magic
import os

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