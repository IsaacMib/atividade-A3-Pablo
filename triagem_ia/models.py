from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Questionario(models.Model):
    """
    Questionário de triagem (ex: M-CHAT, CARS, ABC).
    Define as perguntas e configurações do questionário.
    """
    TIPO_CHOICES = [
        ('mchat', 'M-CHAT (Modified Checklist for Autism in Toddlers)'),
        ('cars', 'CARS (Childhood Autism Rating Scale)'),
        ('abc', 'ABC (Autism Behavior Checklist)'),
        ('outro', 'Outro Questionário'),
    ]
    
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Questionário"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Questionário"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição detalhada do questionário e sua aplicação"
    )
    faixa_etaria_minima = models.IntegerField(
        verbose_name="Idade Mínima (meses)",
        help_text="Idade mínima em meses para aplicação"
    )
    faixa_etaria_maxima = models.IntegerField(
        verbose_name="Idade Máxima (meses)",
        help_text="Idade máxima em meses para aplicação"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
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
        verbose_name = 'Questionário'
        verbose_name_plural = 'Questionários'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Pergunta(models.Model):
    """
    Pergunta individual do questionário.
    """
    TIPO_RESPOSTA_CHOICES = [
        ('sim_nao', 'Sim/Não'),
        ('escala_likert', 'Escala Likert (1-5)'),
        ('multipla_escolha', 'Múltipla Escolha'),
        ('texto_curto', 'Texto Curto'),
    ]
    
    questionario = models.ForeignKey(
        Questionario,
        on_delete=models.CASCADE,
        related_name='perguntas',
        verbose_name="Questionário"
    )
    ordem = models.IntegerField(
        verbose_name="Ordem",
        help_text="Ordem de apresentação da pergunta"
    )
    texto = models.TextField(
        verbose_name="Texto da Pergunta"
    )
    tipo_resposta = models.CharField(
        max_length=20,
        choices=TIPO_RESPOSTA_CHOICES,
        default='sim_nao',
        verbose_name="Tipo de Resposta"
    )
    opcoes_resposta = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Opções de Resposta",
        help_text="JSON com opções para múltipla escolha. Ex: ['Opção 1', 'Opção 2']"
    )
    peso_risco = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name="Peso de Risco",
        help_text="Peso desta pergunta no cálculo de risco (0-10)"
    )
    area_avaliada = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Área Avaliada",
        help_text="Ex: Comunicação, Interação Social, Comportamento"
    )
    
    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['questionario', 'ordem']
        unique_together = ['questionario', 'ordem']
    
    def __str__(self):
        return f"{self.questionario.nome} - Pergunta {self.ordem}"


class Triagem(models.Model):
    """
    Registro de uma triagem completa realizada por um responsável.
    Agrupa respostas do questionário e resultados de análise multimodal.
    """
    STATUS_CHOICES = [
        ('iniciada', 'Iniciada'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_analise', 'Aguardando Análise IA'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    NIVEL_RISCO_CHOICES = [
        ('baixo', 'Baixo Risco'),
        ('moderado', 'Risco Moderado'),
        ('alto', 'Alto Risco'),
        ('muito_alto', 'Risco Muito Alto'),
    ]
    
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='triagens_realizadas',
        verbose_name="Responsável"
    )
    questionario = models.ForeignKey(
        Questionario,
        on_delete=models.PROTECT,
        related_name='triagens',
        verbose_name="Questionário Utilizado"
    )
    nome_crianca = models.CharField(
        max_length=200,
        verbose_name="Nome da Criança"
    )
    data_nascimento_crianca = models.DateField(
        verbose_name="Data de Nascimento da Criança"
    )
    idade_meses = models.IntegerField(
        verbose_name="Idade em Meses",
        help_text="Calculado automaticamente"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='iniciada',
        verbose_name="Status"
    )
    nivel_risco = models.CharField(
        max_length=20,
        choices=NIVEL_RISCO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Nível de Risco"
    )
    pontuacao_total = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Pontuação Total"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações do Responsável"
    )
    iniciada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Iniciada em"
    )
    concluida_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Concluída em"
    )
    
    class Meta:
        verbose_name = 'Triagem'
        verbose_name_plural = 'Triagens'
        ordering = ['-iniciada_em']
    
    def __str__(self):
        return f"Triagem de {self.nome_crianca} - {self.iniciada_em.strftime('%d/%m/%Y')}"
    
    def calcular_idade_meses(self):
        """Calcula idade em meses baseado na data de nascimento."""
        hoje = timezone.now().date()
        meses = (hoje.year - self.data_nascimento_crianca.year) * 12
        meses += hoje.month - self.data_nascimento_crianca.month
        return meses
    
    def save(self, *args, **kwargs):
        """Calcula idade automaticamente antes de salvar."""
        if self.data_nascimento_crianca:
            self.idade_meses = self.calcular_idade_meses()
        super().save(*args, **kwargs)


class RespostaQuestionario(models.Model):
    """
    Resposta individual a uma pergunta do questionário.
    """
    triagem = models.ForeignKey(
        Triagem,
        on_delete=models.CASCADE,
        related_name='respostas',
        verbose_name="Triagem"
    )
    pergunta = models.ForeignKey(
        Pergunta,
        on_delete=models.PROTECT,
        related_name='respostas',
        verbose_name="Pergunta"
    )
    resposta_texto = models.TextField(
        blank=True,
        verbose_name="Resposta em Texto"
    )
    resposta_numerica = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Resposta Numérica",
        help_text="Para escalas Likert ou sim/não (0=não, 1=sim)"
    )
    pontuacao_risco = models.FloatField(
        default=0.0,
        verbose_name="Pontuação de Risco",
        help_text="Calculado baseado no peso da pergunta e resposta"
    )
    respondida_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Respondida em"
    )
    
    class Meta:
        verbose_name = 'Resposta do Questionário'
        verbose_name_plural = 'Respostas do Questionário'
        unique_together = ['triagem', 'pergunta']
    
    def __str__(self):
        return f"Resposta - {self.pergunta.texto[:50]}"


class ModalidadeTexto(models.Model):
    """
    Análise de texto/relatos fornecidos pelo responsável.
    """
    triagem = models.ForeignKey(
        Triagem,
        on_delete=models.CASCADE,
        related_name='analises_texto',
        verbose_name="Triagem"
    )
    texto_relato = models.TextField(
        verbose_name="Relato do Responsável",
        help_text="Descrição de comportamentos observados"
    )
    analise_sentimento = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Análise de Sentimento",
        help_text="Resultado da análise de sentimento (positivo, negativo, neutro)"
    )
    palavras_chave = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Palavras-Chave Extraídas",
        help_text="Lista de palavras-chave relacionadas a TEA"
    )
    score_ia = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Score IA",
        help_text="Probabilidade de indicadores de TEA (0-1)"
    )
    processado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Processado em"
    )
    
    class Meta:
        verbose_name = 'Análise de Texto'
        verbose_name_plural = 'Análises de Texto'
    
    def __str__(self):
        return f"Análise de Texto - Triagem {self.triagem.id}"


class ResultadoIA(models.Model):
    """
    Resultado consolidado da análise multimodal por IA.
    Agrega resultados de texto, áudio e vídeo.
    """
    CONFIANCA_CHOICES = [
        ('muito_baixa', 'Muito Baixa'),
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('muito_alta', 'Muito Alta'),
    ]
    
    triagem = models.OneToOneField(
        Triagem,
        on_delete=models.CASCADE,
        related_name='resultado_ia',
        verbose_name="Triagem"
    )
    probabilidade_tea = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Probabilidade de TEA",
        help_text="Probabilidade calculada pela IA (0-1)"
    )
    confianca = models.CharField(
        max_length=20,
        choices=CONFIANCA_CHOICES,
        verbose_name="Nível de Confiança"
    )
    score_texto = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Score Análise de Texto"
    )
    score_audio = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Score Análise de Áudio"
    )
    score_video = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Score Análise de Vídeo"
    )
    areas_risco = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Áreas de Risco Identificadas",
        help_text="JSON com áreas e scores. Ex: {'comunicacao': 0.8, 'interacao_social': 0.7}"
    )
    recomendacoes = models.TextField(
        blank=True,
        verbose_name="Recomendações",
        help_text="Recomendações geradas pela IA"
    )
    modelo_utilizado = models.CharField(
        max_length=100,
        verbose_name="Modelo de IA Utilizado"
    )
    versao_modelo = models.CharField(
        max_length=50,
        verbose_name="Versão do Modelo"
    )
    processado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Processado em"
    )
    
    class Meta:
        verbose_name = 'Resultado da IA'
        verbose_name_plural = 'Resultados da IA'
    
    def __str__(self):
        return f"Resultado IA - Triagem {self.triagem.id} ({self.probabilidade_tea:.2%})"


class AlertaIA(models.Model):
    """
    Alertas e flags gerados pela IA durante análise.
    Registra comportamentos críticos identificados.
    """
    SEVERIDADE_CHOICES = [
        ('info', 'Informativo'),
        ('atencao', 'Atenção'),
        ('critico', 'Crítico'),
    ]
    
    resultado_ia = models.ForeignKey(
        ResultadoIA,
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name="Resultado IA"
    )
    tipo_alerta = models.CharField(
        max_length=100,
        verbose_name="Tipo de Alerta",
        help_text="Ex: ausencia_contato_visual, estereotipia_motora"
    )
    severidade = models.CharField(
        max_length=20,
        choices=SEVERIDADE_CHOICES,
        verbose_name="Severidade"
    )
    descricao = models.TextField(
        verbose_name="Descrição do Alerta"
    )
    modalidade_origem = models.CharField(
        max_length=20,
        choices=[
            ('texto', 'Texto'),
            ('audio', 'Áudio'),
            ('video', 'Vídeo'),
            ('questionario', 'Questionário'),
        ],
        verbose_name="Modalidade de Origem"
    )
    timestamp_deteccao = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Timestamp de Detecção",
        help_text="Para áudio/vídeo: segundo em que foi detectado"
    )
    confianca_deteccao = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Confiança da Detecção"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    class Meta:
        verbose_name = 'Alerta da IA'
        verbose_name_plural = 'Alertas da IA'
        ordering = ['-severidade', '-confianca_deteccao']
    
    def __str__(self):
        return f"{self.get_severidade_display()} - {self.tipo_alerta}"
