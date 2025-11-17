"""
Admin do app Core.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ConfiguracaoSistema, Log


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    """Admin para Configuração do Sistema"""
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_sistema', 'descricao', 'logo', 'favicon')
        }),
        ('Contato', {
            'fields': ('email_contato', 'telefone', 'endereco')
        }),
        ('Aparência', {
            'fields': ('cor_primaria', 'cor_secundaria'),
            'classes': ('collapse',)
        }),
        ('Redes Sociais', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('Manutenção', {
            'fields': ('manutencao_ativa', 'mensagem_manutencao'),
            'classes': ('collapse',)
        }),
    )
    
    list_display = ['nome_sistema', 'email_contato', 'manutencao_status', 'atualizado_em']
    
    def manutencao_status(self, obj):
        if obj.manutencao_ativa:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ ATIVO</span>'
            )
        return format_html('<span style="color: green;">✓ Desativado</span>')
    manutencao_status.short_description = 'Modo Manutenção'

    def has_add_permission(self, request):
        """Previne criação de múltiplas configurações"""
        return not ConfiguracaoSistema.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Previne deleção da configuração"""
        return False


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    """Admin para Logs"""
    
    list_display = ['tipo', 'acao', 'usuario', 'ip_address', 'criado_em']
    list_filter = ['tipo', 'criado_em']
    search_fields = ['acao', 'descricao', 'usuario__username', 'ip_address']
    readonly_fields = ['usuario', 'tipo', 'acao', 'descricao', 'ip_address', 'user_agent', 'criado_em']
    date_hierarchy = 'criado_em'
    
    def has_add_permission(self, request):
        """Logs são criados automaticamente, não manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs não devem ser editados"""
        return False
