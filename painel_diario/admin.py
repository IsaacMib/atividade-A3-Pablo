from django.contrib import admin
from .models import Crianca, RegistroDiario, MidiaRegistroDiario, TipoTerapia, SessaoTerapia


@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'responsavel', 'data_nascimento', 'idade_display', 'sexo', 'diagnostico_tea', 'ativo']
    list_filter = ['sexo', 'diagnostico_tea', 'ativo']
    search_fields = ['nome', 'responsavel__username']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('responsavel', 'nome', 'data_nascimento', 'sexo', 'foto_perfil')
        }),
        ('Diagnóstico', {
            'fields': ('diagnostico_tea', 'data_diagnostico', 'observacoes_gerais')
        }),
        ('Status', {
            'fields': ('ativo', 'criado_em', 'atualizado_em')
        }),
    )


@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ['crianca', 'data', 'humor_geral', 'horas_sono', 'episodios_crise', 'criado_em']
    list_filter = ['humor_geral', 'qualidade_sono', 'data']
    search_fields = ['crianca__nome', 'observacoes']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['-data']
    date_hierarchy = 'data'
    
    fieldsets = (
        ('Criança e Data', {
            'fields': ('crianca', 'data', 'humor_geral')
        }),
        ('Sono', {
            'fields': ('horas_sono', 'qualidade_sono'),
            'classes': ('collapse',)
        }),
        ('Alimentação', {
            'fields': ('alimentacao_adequada', 'observacoes_alimentacao'),
            'classes': ('collapse',)
        }),
        ('Comunicação', {
            'fields': ('iniciou_comunicacao', 'palavras_novas'),
            'classes': ('collapse',)
        }),
        ('Comportamento', {
            'fields': ('episodios_crise', 'descricao_crises', 'comportamentos_repetitivos', 'descricao_comportamentos'),
            'classes': ('collapse',)
        }),
        ('Interação Social', {
            'fields': ('interacao_outras_criancas', 'contato_visual'),
            'classes': ('collapse',)
        }),
        ('Atividades e Conquistas', {
            'fields': ('atividades_realizadas', 'conquistas_dia', 'observacoes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('criado_por', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MidiaRegistroDiario)
class MidiaRegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ['registro', 'tipo', 'descricao_curta', 'analisado_ia', 'enviado_em']
    list_filter = ['tipo', 'analisado_ia']
    search_fields = ['descricao', 'registro__crianca__nome']
    readonly_fields = ['enviado_em']
    ordering = ['-enviado_em']
    
    def descricao_curta(self, obj):
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao
    descricao_curta.short_description = 'Descrição'


@admin.register(TipoTerapia)
class TipoTerapiaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


@admin.register(SessaoTerapia)
class SessaoTerapiaAdmin(admin.ModelAdmin):
    list_display = ['crianca', 'tipo_terapia', 'profissional_nome', 'data_hora', 'duracao_minutos', 'presenca', 'avaliacao_geral']
    list_filter = ['tipo_terapia', 'presenca', 'data_hora']
    search_fields = ['crianca__nome', 'profissional_nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['-data_hora']
    date_hierarchy = 'data_hora'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('crianca', 'tipo_terapia', 'profissional_nome', 'data_hora', 'duracao_minutos', 'presenca')
        }),
        ('Avaliação da Sessão', {
            'fields': ('objetivos_sessao', 'atividades_realizadas', 'progressos_observados', 'dificuldades_encontradas')
        }),
        ('Observações', {
            'fields': ('observacoes_profissional', 'observacoes_responsavel'),
            'classes': ('collapse',)
        }),
        ('Avaliação Quantitativa', {
            'fields': ('avaliacao_geral', 'engajamento_crianca'),
            'classes': ('collapse',)
        }),
        ('Próxima Sessão', {
            'fields': ('proxima_sessao', 'tarefas_casa'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('criado_por', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
