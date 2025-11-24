from django.contrib import admin
from .models import (
    Questionario, Pergunta, Triagem, RespostaQuestionario,
    ModalidadeTexto, ResultadoIA, AlertaIA
)


@admin.register(Questionario)
class QuestionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'faixa_etaria_minima', 'faixa_etaria_maxima', 'ativo', 'criado_em']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ['questionario', 'ordem', 'texto_curto', 'tipo_resposta', 'peso_risco']
    list_filter = ['questionario', 'tipo_resposta', 'area_avaliada']
    search_fields = ['texto']
    ordering = ['questionario', 'ordem']
    
    def texto_curto(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_curto.short_description = 'Pergunta'


@admin.register(Triagem)
class TriagemAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_crianca', 'responsavel', 'questionario', 'status', 'nivel_risco', 'iniciada_em']
    list_filter = ['status', 'nivel_risco', 'questionario']
    search_fields = ['nome_crianca', 'responsavel__username']
    readonly_fields = ['idade_meses', 'iniciada_em', 'concluida_em']
    ordering = ['-iniciada_em']


@admin.register(RespostaQuestionario)
class RespostaQuestionarioAdmin(admin.ModelAdmin):
    list_display = ['triagem', 'pergunta', 'resposta_numerica', 'pontuacao_risco', 'respondida_em']
    list_filter = ['triagem__questionario']
    search_fields = ['triagem__nome_crianca', 'resposta_texto']
    readonly_fields = ['respondida_em']
    ordering = ['-respondida_em']


@admin.register(ModalidadeTexto)
class ModalidadeTextoAdmin(admin.ModelAdmin):
    list_display = ['triagem', 'score_ia', 'processado_em']
    readonly_fields = ['processado_em']
    ordering = ['-processado_em']


@admin.register(ResultadoIA)
class ResultadoIAAdmin(admin.ModelAdmin):
    list_display = ['triagem', 'probabilidade_tea', 'confianca', 'modelo_utilizado', 'processado_em']
    list_filter = ['confianca']
    readonly_fields = ['processado_em']
    ordering = ['-processado_em']


@admin.register(AlertaIA)
class AlertaIAAdmin(admin.ModelAdmin):
    list_display = ['resultado_ia', 'tipo_alerta', 'severidade', 'modalidade_origem', 'confianca_deteccao', 'criado_em']
    list_filter = ['severidade', 'modalidade_origem']
    search_fields = ['tipo_alerta', 'descricao']
    readonly_fields = ['criado_em']
    ordering = ['-severidade', '-confianca_deteccao']
