from datetime import date
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.conf import settings

from django.core.exceptions import ValidationError
from django.utils.html import escape
import requests
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from blocks.models import ListRedeSocial
from wagtail.models import Page


from django.shortcuts import redirect
from django.contrib import messages


# ==================== MODELOS DE USUÁRIO E LGPD ====================

class PerfilUsuario(models.Model):
    """
    Perfil de usuário para NeuroPrev.
    Extensão do User padrão do Django com campos específicos do sistema.
    
    TODO: Migrar para AUTH_USER_MODEL customizado quando o sistema estiver estável.
    """
    TIPO_USUARIO_CHOICES = [
        ('responsavel', 'Responsável/Pai/Mãe'),
        ('profissional', 'Profissional de Saúde'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name='perfil_neuroprev'
    )
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='responsavel',
        verbose_name="Tipo de Usuário"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone"
    )
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )
    aceite_termos = models.BooleanField(
        default=False,
        verbose_name="Aceite dos Termos de Uso"
    )
    data_aceite_termos = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data do Aceite dos Termos"
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
    
    def __str__(self):
        nome = self.user.get_full_name() or self.user.username
        return f"{nome} ({self.get_tipo_usuario_display()})"


class ConsentimentoLGPD(models.Model):
    """
    Registro de consentimento LGPD do usuário.
    Armazena todas as permissões de uso de dados sensíveis.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name='consentimento_lgpd'
    )
    aceite_coleta_dados = models.BooleanField(
        default=False,
        verbose_name="Aceite de Coleta de Dados"
    )
    aceite_analise_ia = models.BooleanField(
        default=False,
        verbose_name="Aceite de Análise por IA"
    )
    aceite_pesquisa_anonima = models.BooleanField(
        default=False,
        verbose_name="Aceite de Uso em Pesquisa Anônima"
    )
    aceite_compartilhamento_profissionais = models.BooleanField(
        default=False,
        verbose_name="Aceite de Compartilhamento com Profissionais"
    )
    data_aceite = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do Aceite"
    )
    data_revogacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Revogação"
    )
    ip_aceite = models.GenericIPAddressField(
        verbose_name="IP do Aceite"
    )
    
    class Meta:
        verbose_name = 'Consentimento LGPD'
        verbose_name_plural = 'Consentimentos LGPD'
    
    def __str__(self):
        return f"Consentimento de {self.usuario.username}"


class LogAcesso(models.Model):
    """
    Log de acessos a dados sensíveis (auditoria LGPD).
    Registra todas as operações em dados de saúde.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        related_name='logs_acesso'
    )
    acao = models.CharField(
        max_length=100,
        verbose_name="Ação Realizada"
    )
    tabela_acessada = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tabela Acessada"
    )
    objeto_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID do Objeto"
    )
    ip = models.GenericIPAddressField(
        verbose_name="Endereço IP"
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="User Agent"
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data e Hora"
    )
    
    class Meta:
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data_hora}"


class SolicitacaoExclusao(models.Model):
    """
    Solicitações de exclusão de dados (Right to be Forgotten - LGPD).
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_processamento', 'Em Processamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário Solicitante",
        related_name='solicitacoes_exclusao'
    )
    motivo = models.TextField(
        verbose_name="Motivo da Solicitação"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Solicitação"
    )
    data_conclusao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Conclusão"
    )
    processado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exclusoes_processadas',
        verbose_name="Processado Por"
    )
    
    class Meta:
        verbose_name = 'Solicitação de Exclusão'
        verbose_name_plural = 'Solicitações de Exclusão'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação #{self.id} - {self.usuario.username} - {self.get_status_display()}"


# ==================== MODELOS DE PÁGINAS WAGTAIL ====================


class PageSitePadrao(Page):
    """Classe base para todas as páginas do site."""
    
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        help_text="Descrição da página, utilizada em SEO e redes sociais"
    )


    imagem_destaque = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem de Destaque",
        help_text="Imagem usada em destaque para SEO e redes sociais"
    )

    content_panels = Page.content_panels + [
        FieldPanel("descricao"),
        
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("imagem_destaque"),
    ]

    def get_imagem_destaque(self):
        """
        Retorna a imagem de destaque da página ou None se não houver.
        """
        return self.imagem_destaque
    
    def _process_custom_form(self, request):
        """
        Processa formulários customizados presentes no body da página.
        Retorna True se o formulário foi processado com sucesso e deve ser redirecionado,
        False caso contrário.
        """
        from blocks.models import CustomFormBlock
        
        # Procura por um bloco de formulário customizado no body
        form_block = next((block for block in self.body if isinstance(block.block, CustomFormBlock)), None)
        
        if not form_block:
            return False
            
        form = form_block.block.get_context(form_block.value, parent_context={'request': request})['form']
        form_kwargs = {
            'show_recaptcha': getattr(form, 'show_recaptcha', False),
            'recaptcha_secret_key': getattr(form, 'recaptcha_secret_key', None),
            'fields_config': form.fields_config if hasattr(form, 'fields_config') else None,
            'initial': form.initial if hasattr(form, 'initial') else {},
            'request': request,
        }
        bound_form = type(form)(request.POST, request.FILES, **form_kwargs)

        if bound_form.is_valid():
            from blocks.models import FormularioSubmissao, ArquivoSubmetido
            from django.core.files.base import File
            
            field_map = {}
            if hasattr(bound_form, 'fields_config') and bound_form.fields_config:
                for i, block in enumerate(bound_form.fields_config):
                    field_name = f"custom_field_{i}_{block.block_type}"
                    field_label = block.value.get('label', field_name)
                    field_map[field_name] = field_label

            cleaned_data = bound_form.cleaned_data.copy()
            arquivos_para_salvar = {}
            dados_adicionais_serializaveis = {}

            for key, value in cleaned_data.items():
                if isinstance(value, File):
                    arquivos_para_salvar[key] = value
                else:
                    dados_adicionais_serializaveis[field_map.get(key, key)] = value

            nome_completo = cleaned_data.pop('nome_completo', '')
            titulo = cleaned_data.pop('titulo', '')                    

            submissao = FormularioSubmissao.objects.create(
                nome_completo=nome_completo,
                titulo=titulo,
                dados_adicionais={k: v for k, v in dados_adicionais_serializaveis.items() if k not in ['nome_completo', 'titulo', 'g-recaptcha-response']},
                pagina=self,
                usuario=request.user if request.user.is_authenticated else None
            )
            
            for nome_campo, arquivo in arquivos_para_salvar.items():
                ArquivoSubmetido.objects.create(submissao=submissao, nome_campo=nome_campo, arquivo=arquivo)

            messages.success(request, "Formulário Enviado Com Sucesso!")
            return True
        else:
            messages.error(request, "Ocorreu um erro. Por favor, verifique os campos do formulário.")
            setattr(request, '_form_errors', bound_form)
            return False



    class Meta:
        abstract = True


class PageSitePadraoIndex(Page):
    """Classe base para páginas de índice do site."""

    class Meta:
        abstract = True


@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    """Configurações gerais do site."""

    title_suffix = models.CharField(
        verbose_name="Título do Site",
        max_length=255,
        help_text="Título do site e utilizado como sufixo na tag meta. Ex.: ' | NeuroPrev'",
        default="NeuroPrev",
    )

    # --- Redes Sociais e Compartilhamento ---
    redes_sociais = StreamField(
        [("lista_redes", ListRedeSocial())],
        verbose_name="Redes Sociais (Globais)",
        blank=True,
        use_json_field=True,
        help_text="Defina as redes sociais do Portal."
    )

    # --- Menu ---
    menu_max_levels = models.PositiveIntegerField(
        verbose_name="Níveis máximos do menu",
        default=1,
        help_text="Define até quantos níveis de páginas o menu principal irá exibir. (Máximo: 3)"
    )

    # --- Cookies e Analytics ---
    cookies_habilitado = models.BooleanField(
        verbose_name="Habilitar Aviso de Cookies",
        default=False,
        help_text="Ative para exibir o banner de consentimento de cookies no site."
    )
    google_analytics_tag = models.CharField(
        verbose_name="Tag do Google Analytics",
        max_length=20,
        blank=True,
        help_text="Insira a tag do Google Analytics (ex: G-XXXXXXXXXX)."
    )

    # --- Intranet ---
    intranet_habilitada = models.BooleanField(
        default=False,
        verbose_name="Ativar Intranet",
        help_text="Marque esta opção para ativar todas as funcionalidades da Intranet no site."
    )

    # --- Rodapé ---
    footer_titulo_instituicao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Título da Instituição no Rodapé",
        default="CENTRO ADMINISTRATIVO ESTADUAL"
    )
    footer_informacoes = models.TextField(
        blank=True,
        verbose_name="Informações do Rodapé",
        help_text="Endereço, telefone, horário, CNPJ. Use <br> para quebras de linha.",
        default="Rua João da Mata, S/N, Jaguaribe - CEP: 58.015-020<br>\nFone: Recepção: (83) 98658-8328 - JOÃO PESSOA - PARAÍBA<br>\nHorário de Atendimento: Das 8:00 às 16:30<br>\nCNPJ: 09.189.499/0001-00"
    )
    footer_link_sic = models.URLField(
        blank=True,
        verbose_name="Link para o SIC (Serviço de Informação ao Cidadão)",
        default="https://sic.pb.gov.br/"
    )
    footer_imagem_sic = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem do SIC no rodapé",
        help_text="Faça o upload da imagem do logo do SIC."
    )

    captcha_site_key = models.CharField(
        verbose_name="Captcha Site Key (pública)",
        max_length=255,
        blank=True,
        help_text="Chave pública (site key) do reCAPTCHA usada no cliente (frontend)."
    )


    captcha_secret_key = models.CharField(
        verbose_name="Captcha Secret Key (secreta)",
        max_length=255,
        blank=True,
        help_text="Chave secreta do reCAPTCHA usada para validação no servidor. (Deixe em branco se não usar captcha)"
    )

    # Configurações para compartilhamento de conteúdos nas redes sociais
    compartilhamento_habilitado = models.BooleanField(
        verbose_name="Habilitar Compartilhamento",
        default=True,
        help_text="Ative para exibir os botões de compartilhamento nas páginas."
    )
    compartilhamento_facebook = models.BooleanField(
        verbose_name="Facebook",
        default=True,
        help_text="Permitir compartilhamento no Facebook"
    )
    compartilhamento_twitter = models.BooleanField(
        verbose_name="X (Twitter)",
        default=True,
        help_text="Permitir compartilhamento no X (antigo Twitter)"
    )
    compartilhamento_linkedin = models.BooleanField(
        verbose_name="LinkedIn",
        default=True,
        help_text="Permitir compartilhamento no LinkedIn"
    )
    compartilhamento_whatsapp = models.BooleanField(
        verbose_name="WhatsApp",
        default=True,
        help_text="Permitir compartilhamento no WhatsApp"
    )
    compartilhamento_telegram = models.BooleanField(
        verbose_name="Telegram",
        default=False,
        help_text="Permitir compartilhamento no Telegram"
    )
    compartilhamento_email = models.BooleanField(
        verbose_name="E-mail",
        default=True,
        help_text="Permitir compartilhamento via e-mail"
    )
    compartilhamento_copiar_link = models.BooleanField(
        verbose_name="Copiar Link",
        default=True,
        help_text="Permitir copiar o link da página"
    )

    panels = [
        FieldPanel("title_suffix"),
        MultiFieldPanel(
            [
                FieldPanel("redes_sociais"),
            ],
            heading="Redes Sociais"
        ),
        MultiFieldPanel(
            [
                FieldPanel("menu_max_levels"),
            ],
            heading="Menu do Site"
        ),
        MultiFieldPanel(
            [
                FieldPanel("cookies_habilitado"),
                FieldPanel("google_analytics_tag"),
            ],
            heading="Cookies e Analytics"
        ),
        MultiFieldPanel(
            [
                FieldPanel("intranet_habilitada"),
            ],
            heading="Intranet"
        ),
        MultiFieldPanel(
            [
                FieldPanel("footer_titulo_instituicao"),
                FieldPanel("footer_informacoes"),
            ],
            heading="Rodapé",
            classname="collapsible collapsed"
        ),
        MultiFieldPanel(
            [
                FieldPanel("captcha_site_key"),
                FieldPanel("captcha_secret_key"),
            ],
            heading="Captcha (reCAPTCHA)"
        ),
        MultiFieldPanel(
            [
                FieldPanel("compartilhamento_habilitado"),
                FieldPanel("compartilhamento_facebook"),
                FieldPanel("compartilhamento_twitter"),
                FieldPanel("compartilhamento_linkedin"),
                FieldPanel("compartilhamento_whatsapp"),
                FieldPanel("compartilhamento_telegram"),
                FieldPanel("compartilhamento_email"),
                FieldPanel("compartilhamento_copiar_link"),
        ],
        heading="Compartilhamento de Conteúdos"
        ),
    ]

    # --- Validações ---
    def deve_exibir_cookies(self):
        """Retorna True se o aviso de cookies deve ser exibido."""
        return self.cookies_habilitado

    def tem_google_analytics(self):
        """Retorna True se a tag do Google Analytics está configurada."""
        return bool(self.google_analytics_tag and self.google_analytics_tag.strip())

    def deve_exibir_cookies_analytics(self):
        """
        Retorna True se o aviso de cookies analíticos deve ser exibido.
        Só exibe se os cookies estão habilitados E a tag do Google Analytics está definida.
        """
        return self.deve_exibir_cookies() and self.tem_google_analytics()
    
    def tem_captcha_site(self):
        return bool(self.captcha_site_key and self.captcha_site_key.strip())

    def tem_captcha_secret(self):
        return bool(self.captcha_secret_key and self.captcha_secret_key.strip())

    def has_recaptcha_keys(self):
        return self.tem_captcha_site() and self.tem_captcha_secret()

    def get_captcha_site_key(self):
        return self.captcha_site_key.strip() if self.tem_captcha_site() else None

    def get_captcha_secret(self):
        return self.captcha_secret_key.strip() if self.tem_captcha_secret() else None

    def clean(self):
        super().clean()

        if self.menu_max_levels > 3:
            raise ValidationError({
                "menu_max_levels": "O número máximo de níveis permitido para o menu é 3."
            })

        if self.google_analytics_tag:
            tag = self.google_analytics_tag.strip()
            if tag and not (tag.startswith('G-') or tag.startswith('UA-') or tag.startswith('GT-')):
                raise ValidationError({
                    "google_analytics_tag": "A tag deve começar com 'G-', 'UA-' ou 'GT-' seguido do identificador."
                })
            
            if self.captcha_site_key:
                site = self.captcha_site_key.strip()
                if site and len(site) < 10:
                    raise ValidationError({
                        "captcha_site_key": "A site key do captcha parece ser muito curta."
                })
            
    def get_redes_sociais_compartilhamento(self):
        """
        Retorna uma lista das redes sociais habilitadas para compartilhamento.
        """
        redes_habilitadas = []
        
        if not self.compartilhamento_habilitado:
            return redes_habilitadas
            
        if self.compartilhamento_facebook:
            redes_habilitadas.append({
                'nome': 'Facebook',
                'icone': 'fa-brands fa-facebook-f',
                'codigo': 'facebook'
            })
            
        if self.compartilhamento_twitter:
            redes_habilitadas.append({
                'nome': 'X (Twitter)',
                'icone': 'fa-brands fa-square-x-twitter',
                'codigo': 'twitter'
            })
            
        if self.compartilhamento_linkedin:
            redes_habilitadas.append({
                'nome': 'LinkedIn',
                'icone': 'fa-brands fa-linkedin',
                'codigo': 'linkedin'
            })
            
        if self.compartilhamento_whatsapp:
            redes_habilitadas.append({
                'nome': 'WhatsApp',
                'icone': 'fa-brands fa-whatsapp',
                'codigo': 'whatsapp'
            })
            
        if self.compartilhamento_telegram:
            redes_habilitadas.append({
                'nome': 'Telegram',
                'icone': 'fa-brands fa-telegram',
                'codigo': 'telegram'
            })
            
        if self.compartilhamento_email:
            redes_habilitadas.append({
                'nome': 'E-mail',
                'icone': 'fas fa-envelope',
                'codigo': 'email'
            })
            
        if self.compartilhamento_copiar_link:
            redes_habilitadas.append({
                'nome': 'Copiar Link',
                'icone': 'fas fa-link',
                'codigo': 'copy'
            })
            
        return redes_habilitadas

    def tem_compartilhamento_habilitado(self):
        """Retorna True se o compartilhamento está habilitado."""
        return self.compartilhamento_habilitado
   


class ApiSettings(BaseSiteSetting):
    api_habilitada = models.BooleanField(
        verbose_name="Habilitar Integração via API",
        default=False,
        help_text="Marque esta opção para ativar a busca de conteúdo de um portal externo."
    )
    api_url = models.URLField(
        verbose_name="URL da API Externa",
        blank=True,
        help_text="URL base da API do portal de conteúdo externo. Ex:https://paraiba.pb.gov.br/"
    )
    api_usuario = models.CharField(
        max_length=255,
        verbose_name="Usuário da API",
        blank=True,
        help_text="Usuário para autenticação na API externa."
    )
    api_senha = models.CharField(
        max_length=255,
        verbose_name="Senha da API",
        blank=True,
        help_text="Senha para autenticação na API externa. Cuidado: será armazenada como texto plano."
    )

    puxar_noticias = models.BooleanField(
        verbose_name="Consumir Notícias",
        default=False,
        help_text="Ativar para buscar notícias do portal externo."
    )
    tags_noticias = models.CharField(
        max_length=255,
        verbose_name="Tags para filtrar Notícias",
        blank=True,
        help_text="Separar tags por vírgula. Ex: 'geral, importante'. Deixe em branco para buscar todas."
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("api_habilitada"),
                FieldPanel("api_url"),
                FieldPanel("api_usuario"),
                FieldPanel("api_senha", widget=forms.PasswordInput),
            ],
            heading="Integração de Conteúdo Externo"
        ),
        MultiFieldPanel(
            [
                FieldPanel("puxar_noticias"),
                FieldPanel("tags_noticias"),
            ],
            heading="Tipos de Conteúdo para que será consumido",
            classname="collapsible collapsed"
        ),
    ]

    def clean(self):
        super().clean()
        errors = {}

        if self.api_habilitada:
            if not self.api_url:
                errors['api_url'] = ValidationError("A URL da API é obrigatória quando a integração está habilitada.")
            if not self.api_usuario:
                errors['api_usuario'] = ValidationError("O usuário da API é obrigatório quando a integração está habilitada.")
            if not self.api_senha:
                errors['api_senha'] = ValidationError("A senha da API é obrigatória quando a integração está habilitada.")

            if not errors:
                token_url = f"{self.api_url.rstrip('/')}/api/v1/get-token/"
                try:
                    response = requests.post(
                        token_url,
                        data={'username': self.api_usuario, 'password': self.api_senha},
                        timeout=10 
                    )

                    if response.status_code in [400, 401]:
                        errors.update({
                            'api_usuario': ValidationError("Credenciais inválidas. Verifique o usuário e a senha."),
                            'api_senha': ValidationError("Credenciais inválidas. Verifique o usuário e a senha."),
                        })
                    else:
                        response.raise_for_status()
                        if 'token' not in response.json():
                            raise ValidationError("A API não retornou um token de autenticação válido.")
                except requests.exceptions.RequestException as e:
                    errors['api_url'] = ValidationError(f"Não foi possível conectar à API. Verifique a URL. Erro: {e}")

        if getattr(self, "captcha_site_key", None):
            site = self.captcha_site_key.strip()
            if site and len(site) < 10:
                errors["captcha_site_key"] = ValidationError("A site key do captcha parece ser muito curta.")

        if getattr(self, "captcha_secret_key", None):
            secret = self.captcha_secret_key.strip()
            if secret and len(secret) < 10:
                errors["captcha_secret_key"] = ValidationError("A chave secreta do captcha parece ser muito curta.")

        if errors:
            raise ValidationError(errors)

    class Meta:
            verbose_name = "Configurações de Conteúdo Externo"