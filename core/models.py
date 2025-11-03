from datetime import date
from django.db import models
from django import forms

from django.core.exceptions import ValidationError
from django.utils.html import escape
import requests
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from blocks.models import ListRedeSocial, ListRedesSociais
from wagtail.models import Page


from django.shortcuts import redirect
from django.contrib import messages


class PageSitePadrao(Page):
    """Classe base para todas as páginas do site."""
    
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        help_text="Descrição da página para SEO e redes sociais"
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
        help_text="Título do site e utilizado como sufixo na tag meta. Ex.: ' | Site Padrão'",
        default="Site Padrão",
    )

    # --- Período Eleitoral ---
    periodo_eleitoral_habilitado = models.BooleanField(
        verbose_name="Habilitar Período Eleitoral",
        default=False,
        help_text="Ative para indicar que o site está em período eleitoral."
    )
    periodo_eleitoral_inicio = models.DateField(
        verbose_name="Data de início do período eleitoral",
        null=True,
        blank=True
    )
    periodo_eleitoral_fim = models.DateField(
        verbose_name="Data de fim do período eleitoral",
        null=True,
        blank=True
    )
    texto_informativo_periodo_eleitoral = models.TextField(
        verbose_name="Texto informativo do período eleitoral",
        blank=True,
        default="Em respeito à legislação eleitoral (Lei 9.504/97), as notícias deste site/portal estão temporariamente suspensas."
    )

    # --- Redes Sociais e Compartilhamento ---
    redes_sociais = StreamField(
        [("lista_redes", ListRedeSocial())],
        verbose_name="Redes Sociais (Globais)",
        blank=True,
        use_json_field=True,
        help_text="Defina as redes sociais do Portal."
    )

    compartilhar_redes_sociais = models.BooleanField(
        verbose_name="Ativar Compartilhamento em Redes Sociais",
        default=False,
        help_text="Ative para exibir os botões de compartilhamento nas páginas."
    )

    compartilhar_rede_social = StreamField(
        [("redes_compartilhar", ListRedesSociais())],
        verbose_name="Selecionar Redes para Compartilhamento",
        blank=True,
        use_json_field=True,
        help_text=("Escolha quais redes sociais estarão disponíveis para compartilhamento. "
                   "Cada tipo de rede só pode ser adicionado uma vez (máx. 1 por tipo).")
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
                FieldPanel("periodo_eleitoral_habilitado"),
                FieldPanel("periodo_eleitoral_inicio"),
                FieldPanel("periodo_eleitoral_fim"),
                FieldPanel("texto_informativo_periodo_eleitoral"),
            ],
            heading="Período Eleitoral"
        ),
        MultiFieldPanel(
            [
                FieldPanel("redes_sociais"),
                FieldPanel("compartilhar_redes_sociais"),
                FieldPanel("compartilhar_rede_social"),
            ],
            heading="Redes Sociais e Compartilhamento"
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

    def is_periodo_eleitoral(self):
        """
        Retorna True se o período eleitoral está habilitado e a data atual está entre o início e o fim.
        """
        if not self.periodo_eleitoral_habilitado:
            return False
        hoje = date.today()
        if self.periodo_eleitoral_inicio and self.periodo_eleitoral_fim:
            return self.periodo_eleitoral_inicio <= hoje <= self.periodo_eleitoral_fim
        return False

    def get_redes_ativas(self, absolute_url, page_title=None):
        """Gera a lista de redes sociais ativas com URLs de compartilhamento."""
        if not self.compartilhar_redes_sociais or not self.compartilhar_rede_social:
            return []

        redes_ativas = []
        seen_names = set()
        for bloco in self.compartilhar_rede_social:
            # bloco.value can be a list of choice strings (from ListRedesSociais)
            # or a list of Struct values (legacy). Normalize both cases.
            inner = bloco.value
            # If inner is a dict with key 'redes' (StructBlock shape), extract list
            if isinstance(inner, dict) and 'redes' in inner:
                redes_list = inner.get('redes') or []
                # redes_list typically is a list of strings (choice values)
                for nome in redes_list:
                    if not nome:
                        continue
                    # avoid duplicates
                    if nome in seen_names:
                        continue
                    seen_names.add(nome)
                    icone = f"fa-brands fa-{nome}"
                    url = ""
                    # construct sharing URL by type
                    if nome == "messenger":
                        url = f"https://www.facebook.com/dialog/send?link={absolute_url}&app_id=YOUR_APP_ID&redirect_uri={absolute_url}"
                    elif nome == "linkedin":
                        url = f"https://www.linkedin.com/shareArticle?mini=true&url={absolute_url}&title={escape(page_title or '')}"
                    elif nome == "pinterest":
                        url = f"https://pinterest.com/pin/create/button/?url={absolute_url}&description={escape(page_title or '')}"
                    elif nome == "x":
                        url = f"https://twitter.com/intent/tweet?url={absolute_url}&text={escape(page_title or '')}"
                    elif nome == "reddit":
                        url = f"https://www.reddit.com/submit?url={absolute_url}&title={escape(page_title or '')}"
                    elif nome == "whatsapp":
                        url = f"https://api.whatsapp.com/send?text={escape(page_title or '')} {absolute_url}"
                    elif nome == "telegram":
                        url = f"https://t.me/share/url?url={absolute_url}&text={escape(page_title or '')}"
                    elif nome == "email":
                        url = f"mailto:?subject={escape(page_title or '')}&body={absolute_url}"
                    elif nome == "facebook":
                        url = f"https://www.facebook.com/sharer/sharer.php?u={absolute_url}"
                    elif nome == "sms":
                        url = f"sms:?body={escape(page_title or '')} {absolute_url}"
                    elif nome == "print":
                        url = "javascript:window.print();"
                    elif nome == "copy":
                        url = absolute_url

                    redes_ativas.append({"nome": nome, "icone": icone, "url": url})
                continue

            # Otherwise, try to iterate as before over bloco.value items
            for rede in inner:
                # Some stored values may be plain strings or unexpected structures
                # (e.g. older DB migrations). Guard against that by extracting
                # the underlying mapping safely.
                if hasattr(rede, "value"):
                    dados = rede.value
                elif isinstance(rede, dict):
                    dados = rede
                elif isinstance(rede, str):
                    dados = {"nome": rede, "habilitado": True}
                else:
                    # Skip entries we can't interpret as a social item
                    continue

                if not isinstance(dados, dict):
                    continue

                if dados.get("habilitado", False):
                    nome = dados.get("nome")
                    if not nome:
                        continue
                    # avoid duplicates
                    if nome in seen_names:
                        continue
                    seen_names.add(nome)
                    icone = dados.get("icone") or f"fa-brands fa-{nome}"
                    url = ""

                    if nome == "messenger":
                        url = f"https://www.facebook.com/dialog/send?link={absolute_url}&app_id=YOUR_APP_ID&redirect_uri={absolute_url}"
                    elif nome == "linkedin":
                        url = f"https://www.linkedin.com/shareArticle?mini=true&url={absolute_url}&title={escape(page_title or '')}"
                    elif nome == "pinterest":
                        url = f"https://pinterest.com/pin/create/button/?url={absolute_url}&description={escape(page_title or '')}"
                    elif nome == "x":
                        url = f"https://twitter.com/intent/tweet?url={absolute_url}&text={escape(page_title or '')}"
                    elif nome == "reddit":
                        url = f"https://www.reddit.com/submit?url={absolute_url}&title={escape(page_title or '')}"
                    elif nome == "whatsapp":
                        url = f"https://api.whatsapp.com/send?text={escape(page_title or '')} {absolute_url}"
                    elif nome == "telegram":
                        url = f"https://t.me/share/url?url={absolute_url}&text={escape(page_title or '')}"
                    elif nome == "email":
                        url = f"mailto:?subject={escape(page_title or '')}&body={absolute_url}"
                    elif nome == "facebook":
                        url = f"https://www.facebook.com/sharer/sharer.php?u={absolute_url}"
                    elif nome == "sms":
                        url = f"sms:?body={escape(page_title or '')} {absolute_url}"
                    elif nome == "print":
                        url = "javascript:window.print();"
                    elif nome == "copy":
                        url = absolute_url

                    redes_ativas.append({"nome": nome, "icone": icone, "url": url})

        return redes_ativas

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

        # Validate compartilhar_rede_social: ensure no duplicate network types
        try:
            selected = []
            for bloco in self.compartilhar_rede_social:
                inner = bloco.value
                if isinstance(inner, dict) and 'redes' in inner:
                    redes_list = inner.get('redes') or []
                    for nome in redes_list:
                        if nome:
                            selected.append(nome)
                else:
                    # iterate items if list-like
                    try:
                        for item in inner:
                            if hasattr(item, 'value') and isinstance(item.value, dict):
                                nome = item.value.get('nome')
                                if nome:
                                    selected.append(nome)
                            elif isinstance(item, str):
                                selected.append(item)
                    except Exception:
                        # ignore unexpected shapes here; will be caught earlier if needed
                        pass

            # find duplicates
            from collections import Counter
            counts = Counter(selected)
            duplicates = [k for k, v in counts.items() if v > 1]
            if duplicates:
                raise ValidationError({
                    'compartilhar_rede_social': ValidationError(
                        f"Duplicatas encontradas nas redes de compartilhamento: {', '.join(duplicates)}. Remova duplicatas (máx. 1 de cada tipo)."
                    )
                })
        except Exception:
            # don't break saving for unexpected shapes; be conservative and allow save
            pass


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

        if self.periodo_eleitoral_habilitado:
            if not self.periodo_eleitoral_inicio and not self.periodo_eleitoral_fim:
                raise ValidationError({
                    "periodo_eleitoral_inicio": "Obrigatório quando o período eleitoral está habilitado.",
                    "periodo_eleitoral_fim": "Obrigatório quando o período eleitoral está habilitado.",
                })
            if not self.periodo_eleitoral_inicio:
                raise ValidationError({
                    "periodo_eleitoral_inicio": "Obrigatório quando o período eleitoral está habilitado."
                })
            if not self.periodo_eleitoral_fim:
                raise ValidationError({
                    "periodo_eleitoral_fim": "Obrigatório quando o período eleitoral está habilitado."
                })
            if self.periodo_eleitoral_inicio > self.periodo_eleitoral_fim:
                raise ValidationError({
                    "periodo_eleitoral_inicio": "A data de início não pode ser posterior à data de fim.",
                    "periodo_eleitoral_fim": "A data de fim não pode ser anterior à data de início."
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