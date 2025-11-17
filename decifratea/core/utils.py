"""
Funções utilitárias do app Core.
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional

from django.core.files.storage import default_storage
from django.utils.text import slugify


def gerar_slug_unico(texto: str, model_class, campo_slug: str = 'slug') -> str:
    """
    Gera um slug único para um model.
    
    Args:
        texto: Texto base para gerar o slug
        model_class: Classe do model
        campo_slug: Nome do campo slug no model
    
    Returns:
        Slug único
    """
    slug_base = slugify(texto)
    slug = slug_base
    contador = 1
    
    filtro = {f'{campo_slug}': slug}
    while model_class.objects.filter(**filtro).exists():
        slug = f'{slug_base}-{contador}'
        contador += 1
        filtro = {f'{campo_slug}': slug}
    
    return slug


def formatar_telefone(telefone: str) -> str:
    """
    Formata um número de telefone brasileiro.
    
    Args:
        telefone: Número de telefone
    
    Returns:
        Telefone formatado
    """
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, telefone))
    
    if len(numeros) == 11:
        # Celular: (XX) X XXXX-XXXX
        return f'({numeros[:2]}) {numeros[2]} {numeros[3:7]}-{numeros[7:]}'
    elif len(numeros) == 10:
        # Fixo: (XX) XXXX-XXXX
        return f'({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}'
    
    return telefone


def formatar_cpf(cpf: str) -> str:
    """
    Formata um CPF.
    
    Args:
        cpf: CPF sem formatação
    
    Returns:
        CPF formatado
    """
    numeros = ''.join(filter(str.isdigit, cpf))
    
    if len(numeros) == 11:
        return f'{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}'
    
    return cpf


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata um CNPJ.
    
    Args:
        cnpj: CNPJ sem formatação
    
    Returns:
        CNPJ formatado
    """
    numeros = ''.join(filter(str.isdigit, cnpj))
    
    if len(numeros) == 14:
        return f'{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}'
    
    return cnpj


def calcular_hash_arquivo(arquivo) -> str:
    """
    Calcula o hash MD5 de um arquivo.
    
    Args:
        arquivo: Objeto de arquivo
    
    Returns:
        Hash MD5 do arquivo
    """
    md5 = hashlib.md5()
    
    if hasattr(arquivo, 'read'):
        for chunk in arquivo.chunks():
            md5.update(chunk)
        arquivo.seek(0)
    
    return md5.hexdigest()


def obter_tamanho_arquivo_formatado(tamanho_bytes: int) -> str:
    """
    Formata o tamanho de arquivo em uma string legível.
    
    Args:
        tamanho_bytes: Tamanho em bytes
    
    Returns:
        Tamanho formatado (ex: "1.5 MB")
    """
    for unidade in ['B', 'KB', 'MB', 'GB', 'TB']:
        if tamanho_bytes < 1024.0:
            return f"{tamanho_bytes:.1f} {unidade}"
        tamanho_bytes /= 1024.0
    
    return f"{tamanho_bytes:.1f} PB"


def get_client_ip(request) -> Optional[str]:
    """
    Obtém o IP real do cliente.
    
    Args:
        request: Request do Django
    
    Returns:
        IP do cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def limpar_arquivos_antigos(diretorio: str, dias: int = 30):
    """
    Remove arquivos mais antigos que X dias de um diretório.
    
    Args:
        diretorio: Caminho do diretório
        dias: Número de dias
    """
    data_limite = datetime.now() - timedelta(days=dias)
    
    try:
        diretorios, arquivos = default_storage.listdir(diretorio)
        
        for arquivo in arquivos:
            caminho_completo = os.path.join(diretorio, arquivo)
            
            try:
                # Verifica data de modificação
                modificado = default_storage.get_modified_time(caminho_completo)
                
                if modificado.replace(tzinfo=None) < data_limite:
                    default_storage.delete(caminho_completo)
            except Exception:
                continue
                
    except Exception:
        pass


def truncar_texto(texto: str, limite: int = 100, sufixo: str = '...') -> str:
    """
    Trunca um texto adicionando sufixo se necessário.
    
    Args:
        texto: Texto a truncar
        limite: Limite de caracteres
        sufixo: Sufixo a adicionar
    
    Returns:
        Texto truncado
    """
    if len(texto) <= limite:
        return texto
    
    return texto[:limite - len(sufixo)] + sufixo
