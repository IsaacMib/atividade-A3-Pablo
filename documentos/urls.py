from django.urls import path
from .views import DocumentServeView, document_serve_inline

app_name = 'documentos'

urlpatterns = [
    # View customizada para servir documentos inline (classe)
    path('view/<int:document_id>/<str:document_filename>', DocumentServeView.as_view(), name='document_serve_inline'),
    
    # View alternativa (função)
    # path('view/<int:document_id>/<str:document_filename>', document_serve_inline, name='document_serve_inline'),
]