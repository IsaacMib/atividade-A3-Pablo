"""
Models do app Core.
Contém models base e configurações globais do sistema.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class ModelBase(models.Model):
    """
    Model abstrato base para todos os models do sistema.
    Adiciona campos comuns de auditoria.
    """
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_criado",
        verbose_name="Criado por"
    )
    atualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_atualizado",
        verbose_name="Atualizado por"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        abstract = True
        ordering = ['-criado_em']

    def save(self, *args, **kwargs):
        """Override para adicionar validações customizadas"""
        self.full_clean()
        super().save(*args, **kwargs)


class ConfiguracaoSistema(models.Model):
    """
    Configurações globais do sistema.
    Singleton - só deve existir uma instância.
    """
    nome_sistema = models.CharField(
        max_length=200,
        default="Gestão de Estoque",
        verbose_name="Nome do Sistema"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    email_contato = models.EmailField(
        blank=True,
        verbose_name="Email de Contato"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone"
    )
    endereco = models.TextField(
        blank=True,
        verbose_name="Endereço"
    )
    logo = models.ImageField(
        upload_to='configuracao/',
        null=True,
        blank=True,
        verbose_name="Logo"
    )
    favicon = models.ImageField(
        upload_to='configuracao/',
        null=True,
        blank=True,
        verbose_name="Favicon"
    )
    
    # Configurações de aparência
    cor_primaria = models.CharField(
        max_length=7,
        default="#0ea5e9",
        help_text="Cor primária do sistema (hex)",
        verbose_name="Cor Primária"
    )
    cor_secundaria = models.CharField(
        max_length=7,
        default="#0284c7",
        help_text="Cor secundária do sistema (hex)",
        verbose_name="Cor Secundária"
    )
    
    # Redes sociais
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn")
    
    # Configurações técnicas
    manutencao_ativa = models.BooleanField(
        default=False,
        verbose_name="Modo Manutenção",
        help_text="Quando ativo, o sistema exibe mensagem de manutenção"
    )
    mensagem_manutencao = models.TextField(
        blank=True,
        default="Sistema em manutenção. Voltaremos em breve.",
        verbose_name="Mensagem de Manutenção"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"

    def __str__(self):
        return self.nome_sistema

    def save(self, *args, **kwargs):
        """Garante que só exista uma instância (singleton)"""
        if not self.pk and ConfiguracaoSistema.objects.exists():
            raise ValidationError('Já existe uma configuração do sistema.')
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Retorna a instância única de configuração"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Log(models.Model):
    """
    Log de ações importantes do sistema.
    """
    TIPO_CHOICES = [
        ('INFO', 'Informação'),
        ('WARNING', 'Aviso'),
        ('ERROR', 'Erro'),
        ('CRITICAL', 'Crítico'),
        ('SUCCESS', 'Sucesso'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='INFO',
        verbose_name="Tipo"
    )
    acao = models.CharField(
        max_length=200,
        verbose_name="Ação"
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora"
    )

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.tipo} - {self.acao} - {self.criado_em}"

    @classmethod
    def registrar(cls, acao, tipo='INFO', descricao='', usuario=None, request=None):
        """
        Método auxiliar para criar logs facilmente.
        """
        log_data = {
            'acao': acao,
            'tipo': tipo,
            'descricao': descricao,
            'usuario': usuario,
        }
        
        if request:
            log_data['ip_address'] = cls.get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(**log_data)

    @staticmethod
    def get_client_ip(request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
