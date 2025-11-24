from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Crianca(models.Model):
    """
    Perfil da criança sendo acompanhada.
    Centraliza informações e vincula aos registros diários.
    """
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='criancas',
        verbose_name="Responsável"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome"
    )
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento"
    )
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name="Sexo"
    )
    foto_perfil = models.ImageField(
        upload_to='criancas/fotos/',
        null=True,
        blank=True,
        verbose_name="Foto de Perfil"
    )
    diagnostico_tea = models.BooleanField(
        default=False,
        verbose_name="Diagnóstico de TEA",
        help_text="Indica se a criança já possui diagnóstico de TEA"
    )
    data_diagnostico = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do Diagnóstico"
    )
    observacoes_gerais = models.TextField(
        blank=True,
        verbose_name="Observações Gerais",
        help_text="Informações relevantes sobre a criança"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Perfil ativo para registro"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = 'Criança'
        verbose_name_plural = 'Crianças'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def calcular_idade(self):
        """Retorna idade em anos e meses."""
        hoje = timezone.now().date()
        anos = hoje.year - self.data_nascimento.year
        meses = hoje.month - self.data_nascimento.month
        
        if meses < 0:
            anos -= 1
            meses += 12
        
        return {'anos': anos, 'meses': meses}
    
    def idade_display(self):
        """Retorna idade formatada."""
        idade = self.calcular_idade()
        return f"{idade['anos']} anos e {idade['meses']} meses"


class RegistroDiario(models.Model):
    """
    Registro diário de comportamentos e desenvolvimento da criança.
    Core do sistema de acompanhamento.
    """
    HUMOR_CHOICES = [
        ('muito_feliz', '😄 Muito Feliz'),
        ('feliz', '🙂 Feliz'),
        ('neutro', '😐 Neutro'),
        ('triste', '😢 Triste'),
        ('irritado', '😠 Irritado'),
    ]
    
    QUALIDADE_SONO_CHOICES = [
        ('excelente', 'Excelente'),
        ('boa', 'Boa'),
        ('regular', 'Regular'),
        ('ruim', 'Ruim'),
    ]
    
    crianca = models.ForeignKey(
        Crianca,
        on_delete=models.CASCADE,
        related_name='registros_diarios',
        verbose_name="Criança"
    )
    data = models.DateField(
        verbose_name="Data do Registro"
    )
    humor_geral = models.CharField(
        max_length=20,
        choices=HUMOR_CHOICES,
        verbose_name="Humor Geral do Dia"
    )
    
    # Sono
    horas_sono = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        verbose_name="Horas de Sono"
    )
    qualidade_sono = models.CharField(
        max_length=20,
        choices=QUALIDADE_SONO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Qualidade do Sono"
    )
    
    # Alimentação
    alimentacao_adequada = models.BooleanField(
        default=True,
        verbose_name="Alimentação Adequada",
        help_text="A criança se alimentou adequadamente?"
    )
    observacoes_alimentacao = models.TextField(
        blank=True,
        verbose_name="Observações sobre Alimentação"
    )
    
    # Comunicação
    iniciou_comunicacao = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Iniciativas de Comunicação",
        help_text="Número de vezes que iniciou comunicação espontânea"
    )
    palavras_novas = models.TextField(
        blank=True,
        verbose_name="Palavras ou Frases Novas",
        help_text="Registre palavras ou frases novas usadas hoje"
    )
    
    # Comportamento
    episodios_crise = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Episódios de Crise",
        help_text="Número de crises ou birras"
    )
    descricao_crises = models.TextField(
        blank=True,
        verbose_name="Descrição das Crises",
        help_text="Contexto e gatilhos das crises"
    )
    comportamentos_repetitivos = models.BooleanField(
        default=False,
        verbose_name="Comportamentos Repetitivos Observados"
    )
    descricao_comportamentos = models.TextField(
        blank=True,
        verbose_name="Descrição dos Comportamentos"
    )
    
    # Interação Social
    interacao_outras_criancas = models.BooleanField(
        default=False,
        verbose_name="Interagiu com Outras Crianças"
    )
    contato_visual = models.CharField(
        max_length=20,
        choices=[
            ('frequente', 'Frequente'),
            ('ocasional', 'Ocasional'),
            ('raro', 'Raro'),
            ('ausente', 'Ausente'),
        ],
        null=True,
        blank=True,
        verbose_name="Contato Visual"
    )
    
    # Atividades
    atividades_realizadas = models.TextField(
        blank=True,
        verbose_name="Atividades Realizadas",
        help_text="Brincadeiras, terapias, passeios, etc."
    )
    
    # Observações gerais
    conquistas_dia = models.TextField(
        blank=True,
        verbose_name="Conquistas do Dia",
        help_text="Marcos ou progressos observados"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações Gerais"
    )
    
    # Metadata
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_criados',
        verbose_name="Criado Por"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = 'Registro Diário'
        verbose_name_plural = 'Registros Diários'
        ordering = ['-data']
        unique_together = ['crianca', 'data']
    
    def __str__(self):
        return f"Registro de {self.crianca.nome} - {self.data.strftime('%d/%m/%Y')}"


class MidiaRegistroDiario(models.Model):
    """
    Mídias anexadas ao registro diário (fotos, vídeos, áudios).
    Permite análise multimodal posterior.
    """
    TIPO_MIDIA_CHOICES = [
        ('foto', 'Foto'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
    ]
    
    registro = models.ForeignKey(
        RegistroDiario,
        on_delete=models.CASCADE,
        related_name='midias',
        verbose_name="Registro Diário"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_MIDIA_CHOICES,
        verbose_name="Tipo de Mídia"
    )
    arquivo = models.FileField(
        upload_to='registros_diarios/midias/%Y/%m/',
        verbose_name="Arquivo"
    )
    descricao = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Descrição",
        help_text="Breve descrição do que está sendo registrado"
    )
    duracao_segundos = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Duração (segundos)",
        help_text="Para vídeos e áudios"
    )
    analisado_ia = models.BooleanField(
        default=False,
        verbose_name="Analisado por IA"
    )
    resultado_analise = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Resultado da Análise",
        help_text="Resultado da análise de IA da mídia"
    )
    enviado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Enviado em"
    )
    
    class Meta:
        verbose_name = 'Mídia do Registro'
        verbose_name_plural = 'Mídias dos Registros'
        ordering = ['-enviado_em']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.registro}"


class TipoTerapia(models.Model):
    """
    Tipos de terapias e intervenções (ABA, Fonoaudiologia, TO, etc.).
    """
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome da Terapia"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    cor = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name="Cor",
        help_text="Cor para representação visual (hex). Ex: #3498db"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = 'Tipo de Terapia'
        verbose_name_plural = 'Tipos de Terapias'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class SessaoTerapia(models.Model):
    """
    Registro de sessão individual de terapia.
    Acompanhamento de frequência e evolução nas terapias.
    """
    PRESENCA_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('cancelada', 'Cancelada'),
    ]
    
    crianca = models.ForeignKey(
        Crianca,
        on_delete=models.CASCADE,
        related_name='sessoes_terapia',
        verbose_name="Criança"
    )
    tipo_terapia = models.ForeignKey(
        TipoTerapia,
        on_delete=models.PROTECT,
        related_name='sessoes',
        verbose_name="Tipo de Terapia"
    )
    profissional_nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Profissional"
    )
    data_hora = models.DateTimeField(
        verbose_name="Data e Hora da Sessão"
    )
    duracao_minutos = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Duração (minutos)"
    )
    presenca = models.CharField(
        max_length=20,
        choices=PRESENCA_CHOICES,
        default='presente',
        verbose_name="Presença"
    )
    
    # Avaliação da sessão
    objetivos_sessao = models.TextField(
        blank=True,
        verbose_name="Objetivos da Sessão"
    )
    atividades_realizadas = models.TextField(
        blank=True,
        verbose_name="Atividades Realizadas"
    )
    progressos_observados = models.TextField(
        blank=True,
        verbose_name="Progressos Observados"
    )
    dificuldades_encontradas = models.TextField(
        blank=True,
        verbose_name="Dificuldades Encontradas"
    )
    observacoes_profissional = models.TextField(
        blank=True,
        verbose_name="Observações do Profissional"
    )
    observacoes_responsavel = models.TextField(
        blank=True,
        verbose_name="Observações do Responsável"
    )
    
    # Avaliação quantitativa
    avaliacao_geral = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Avaliação Geral (1-5)",
        help_text="1=Muito difícil, 5=Excelente progresso"
    )
    engajamento_crianca = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Engajamento da Criança (1-5)"
    )
    
    # Próxima sessão
    proxima_sessao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Próxima Sessão Agendada"
    )
    tarefas_casa = models.TextField(
        blank=True,
        verbose_name="Tarefas para Casa",
        help_text="Atividades para o responsável realizar em casa"
    )
    
    # Metadata
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sessoes_terapia_criadas',
        verbose_name="Registrado Por"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = 'Sessão de Terapia'
        verbose_name_plural = 'Sessões de Terapia'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.tipo_terapia.nome} - {self.crianca.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
