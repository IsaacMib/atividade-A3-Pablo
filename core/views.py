from django.shortcuts import render, get_object_or_404
from django.http import Http404, FileResponse
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.utils.decorators import method_decorator
from wagtail.documents.models import Document
import mimetypes
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_sameorigin, name='dispatch')
class DocumentServeView(View):
    """
    View reutilizável para servir documentos com Content-Disposition: inline
    permitindo visualização no browser em vez de forçar download.
    
    Pode ser usada em qualquer app do projeto através das URLs do core.
    """
    
    @method_decorator(cache_control(max_age=3600))
    def get(self, request, document_id, document_filename):
        logger.info(f"Serving document {document_id}: {document_filename}")
        
        try:
            # Busca o documento pelo ID
            document = get_object_or_404(Document, id=document_id)
            
            # Verifica se o filename corresponde
            if document.filename != document_filename:
                logger.warning(f"Filename mismatch: expected {document.filename}, got {document_filename}")
                raise Http404("Document not found")
            
            # Verifica se o arquivo existe
            if not document.file:
                logger.warning(f"No file for document {document_id}")
                raise Http404("Document file not found")
            
            # Determina o content type
            content_type, _ = mimetypes.guess_type(document.filename)
            file_ext = document.filename.lower().split('.')[-1] if '.' in document.filename else ''
            
            # Define content types específicos para melhor compatibilidade
            if file_ext == 'pdf':
                content_type = 'application/pdf'
            elif file_ext in ['jpg', 'jpeg']:
                content_type = 'image/jpeg'
            elif file_ext == 'png':
                content_type = 'image/png'
            elif file_ext == 'gif':
                content_type = 'image/gif'
            elif file_ext == 'webp':
                content_type = 'image/webp'
            elif file_ext in ['doc', 'docx']:
                content_type = 'application/msword' if file_ext == 'doc' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_ext in ['xls', 'xlsx']:
                content_type = 'application/vnd.ms-excel' if file_ext == 'xls' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif not content_type:
                content_type = 'application/octet-stream'
            
            logger.info(f"Serving {document.filename} as {content_type}")
            
            # Usa FileResponse que é mais eficiente para arquivos grandes
            response = FileResponse(
                document.file.open('rb'),
                content_type=content_type,
                filename=document.filename
            )
            
            # Headers básicos para visualização inline
            response['Content-Disposition'] = f'inline; filename="{document.filename}"'
            response['X-Content-Type-Options'] = 'nosniff'
            
            # O X-Frame-Options é definido pelo decorator xframe_options_sameorigin
            
            # Headers específicos para diferentes tipos de arquivo
            if file_ext == 'pdf':
                response['Cache-Control'] = 'public, max-age=3600'
                response['X-PDF-Options'] = 'inline'
                # Headers adicionais para PDFs em iframes
                response['Content-Security-Policy'] = "frame-ancestors 'self'"
                response['Referrer-Policy'] = 'same-origin'
            elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                response['Cache-Control'] = 'public, max-age=86400'  # 24h para imagens
            elif file_ext in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
                # Office docs podem ter problemas com inline, forçamos attachment
                response['Content-Disposition'] = f'attachment; filename="{document.filename}"'
                response['Cache-Control'] = 'no-cache'
            else:
                response['Cache-Control'] = 'public, max-age=1800'  # 30min para outros
            
            # Para desenvolvimento, permite CORS
            response['Access-Control-Allow-Origin'] = '*'
            
            return response
            
        except Exception as e:
            logger.error(f"Error serving document {document_id}: {str(e)}")
            raise Http404(f"Error serving document: {str(e)}")


@cache_control(max_age=3600)
@xframe_options_sameorigin
def document_serve_inline(request, document_id, document_filename):
    """
    Função view alternativa para servir documentos inline.
    Versão mais simples da DocumentServeView para casos básicos.
    """
    document = get_object_or_404(Document, id=document_id)
    
    if document.filename != document_filename:
        raise Http404("Document not found")
    
    if not document.file:
        raise Http404("Document file not found")
    
    try:
        content_type, _ = mimetypes.guess_type(document.filename)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Para PDFs, força o content type correto
        if document.filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        
        response = FileResponse(
            document.file.open('rb'),
            content_type=content_type,
            filename=document.filename
        )
        
        response['Content-Disposition'] = f'inline; filename="{document.filename}"'
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Exception as e:
        raise Http404(f"Error serving document: {str(e)}")

