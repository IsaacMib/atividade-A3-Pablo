# NeuroPrev Multimodal - Arquitetura do Sistema

**Sistema de Triagem Precoce de Autismo com Inteligência Artificial Multimodal**

*Versão: 1.0.0 (MVP)*  
*Data: 24/11/2025*

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura Técnica](#arquitetura-técnica)
3. [Módulos do Sistema](#módulos-do-sistema)
4. [Fluxo de Dados](#fluxo-de-dados)
5. [Segurança e LGPD](#segurança-e-lgpd)
6. [Roadmap de Desenvolvimento](#roadmap-de-desenvolvimento)

---

## 🎯 Visão Geral

### Objetivo
Criar uma plataforma científica e comercialmente viável para **triagem precoce de Transtorno do Espectro Autista (TEA)** em crianças, integrando **Inteligência Artificial Multimodal** com múltiplas fontes de dados:

- ✅ **Texto**: Questionários estruturados + relatos livres
- ✅ **Imagem/Vídeo**: Expressões faciais, contato visual, movimentos
- ✅ **Áudio**: Prosódia, ritmo, ecolalia
- ✅ **Temporal**: Evolução de comportamento ao longo do tempo

### Público-Alvo

1. **Pais/Responsáveis**: Ferramenta de triagem e acompanhamento diário
2. **Profissionais de Saúde**: Dashboard de evolução e suporte clínico (futuro)
3. **Pesquisadores**: Dados anônimos para estudos científicos (futuro)

### Base Científica

Baseado na pesquisa:  
**"A multimodular approach to streamline autism diagnosis in young children"**

Instrumentos de triagem validados:
- M-CHAT-R (Modified Checklist for Autism in Toddlers, Revised)
- Q-CHAT (Quantitative Checklist for Autism in Toddlers)
- Escalas de desenvolvimento sensorial e motor

---

## 🏗️ Arquitetura Técnica

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  HTML5 + Sass + JavaScript + Webpack + Bootstrap           │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND                               │
│  Django 5.1 + Wagtail 7.x + Django REST Framework          │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│ PostgreSQL  │    │  IA Multimodal  │    │  Celery +   │
│  (Produção) │    │  (TensorFlow/   │    │  Redis      │
│             │    │   PyTorch)      │    │  (Tarefas)  │
└─────────────┘    └─────────────────┘    └─────────────┘
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  AWS S3/MinIO   │
                    │  (Mídia/Vídeos) │
                    └─────────────────┘
```

### Banco de Dados

- **Produção**: PostgreSQL 14+
- **Desenvolvimento**: SQLite (mantido para testes rápidos)
- **Mídia**: S3-compatible (AWS S3 ou MinIO para dev)

### Ambiente Python

- **Python**: 3.12+
- **Framework**: Django 5.1.14
- **CMS**: Wagtail 7.x
- **API**: Django REST Framework 3.15+
- **IA**: TensorFlow 2.x ou PyTorch 2.x
- **Tarefas Assíncronas**: Celery + Redis

---

## 📦 Módulos do Sistema

### MÓDULO 1: Triagem Multimodal (`triagem_ia/`)

**Objetivo**: Core do sistema de IA multimodal para análise de risco de TEA.

#### 1.1. Modelos de Dados

```python
# triagem_ia/models.py

class Questionario(models.Model):
    """
    Questionários estruturados (M-CHAT-R, Q-CHAT, custom)
    """
    nome = models.CharField(max_length=200)  # "M-CHAT-R", "Q-CHAT"
    versao = models.CharField(max_length=50)
    tipo = models.CharField(choices=[
        ('mchat', 'M-CHAT-R'),
        ('qchat', 'Q-CHAT'),
        ('desenvolvimento', 'Desenvolvimento Geral'),
        ('sensorial', 'Perfil Sensorial'),
        ('custom', 'Personalizado'),
    ])
    ativo = models.BooleanField(default=True)
    
class Pergunta(models.Model):
    """
    Perguntas de cada questionário
    """
    questionario = models.ForeignKey(Questionario)
    ordem = models.IntegerField()
    texto = models.TextField()
    tipo_resposta = models.CharField(choices=[
        ('sim_nao', 'Sim/Não'),
        ('escala', 'Escala Likert'),
        ('multipla', 'Múltipla Escolha'),
        ('texto_livre', 'Texto Livre'),
    ])
    peso = models.FloatField(default=1.0)  # Peso na análise
    categoria = models.CharField()  # Linguagem, Social, Motor, etc.

class Triagem(models.Model):
    """
    Sessão de triagem de uma criança
    """
    crianca = models.ForeignKey('Crianca')
    responsavel = models.ForeignKey('auth.User')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True)
    status = models.CharField(choices=[
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('analisando', 'Analisando com IA'),
        ('finalizada', 'Finalizada com Resultado'),
    ])
    
class RespostaQuestionario(models.Model):
    """
    Respostas de cada pergunta
    """
    triagem = models.ForeignKey(Triagem)
    pergunta = models.ForeignKey(Pergunta)
    resposta_texto = models.TextField(null=True)
    resposta_escala = models.IntegerField(null=True)
    resposta_booleana = models.BooleanField(null=True)
    observacoes = models.TextField(blank=True)

class ModalidadeTexto(models.Model):
    """
    Análise de texto (relatos + questionários)
    """
    triagem = models.OneToOneField(Triagem)
    relato_livre = models.TextField()
    palavras_chave_detectadas = models.JSONField()  # ["atraso", "não responde", etc.]
    sentimentos_detectados = models.JSONField()  # {"preocupacao": 0.8, "ansiedade": 0.6}
    score_texto = models.FloatField()  # 0-1

class ModalidadeImagem(models.Model):
    """
    Análise de imagens/vídeos (futuro)
    """
    triagem = models.ForeignKey(Triagem)
    arquivo = models.FileField(upload_to='triagem/imagens/')
    tipo = models.CharField(choices=[
        ('foto', 'Foto'),
        ('video', 'Vídeo'),
    ])
    analise_facial = models.JSONField()  # {"contato_visual": 0.3, "sorriso": 0.6}
    movimentos_repetitivos = models.BooleanField(default=False)
    score_visual = models.FloatField()

class ModalidadeAudio(models.Model):
    """
    Análise de áudio (futuro)
    """
    triagem = models.ForeignKey(Triagem)
    arquivo = models.FileField(upload_to='triagem/audios/')
    transcricao = models.TextField()
    prosódia_score = models.FloatField()
    ecolalia_detectada = models.BooleanField()
    ritmo_score = models.FloatField()
    score_audio = models.FloatField()

class ResultadoIA(models.Model):
    """
    Resultado final da análise multimodal
    """
    triagem = models.OneToOneField(Triagem)
    probabilidade_risco = models.FloatField()  # 0-100%
    nivel_risco = models.CharField(choices=[
        ('baixo', 'Baixo Risco'),
        ('moderado', 'Risco Moderado'),
        ('alto', 'Alto Risco - Avaliação Profissional Recomendada'),
    ])
    perfil_comportamental = models.JSONField()  # {"social": 0.4, "linguagem": 0.7, ...}
    sinais_identificados = models.JSONField()  # ["Pouco contato visual", "Não responde ao nome"]
    recomendacoes = models.TextField()
    data_analise = models.DateTimeField(auto_now_add=True)
    versao_modelo_ia = models.CharField(max_length=50)  # "v1.0.0"

class AlertaIA(models.Model):
    """
    Alertas automáticos da IA
    """
    triagem = models.ForeignKey(Triagem)
    tipo = models.CharField(choices=[
        ('regressao', 'Regressão de Habilidades'),
        ('urgente', 'Sinais de Urgência'),
        ('avanco', 'Avanço Significativo'),
        ('info', 'Informativo'),
    ])
    mensagem = models.TextField()
    visualizado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
```

#### 1.2. Funcionalidades

- ✅ Questionários M-CHAT-R e Q-CHAT
- ✅ Relatos livres dos pais
- ✅ Histórico perinatal
- ⏳ Upload de fotos/vídeos (MVP v2)
- ⏳ Upload de áudios (MVP v2)
- ✅ Análise multimodal com fusão de dados
- ✅ Geração de relatório de risco
- ✅ Alertas automáticos

#### 1.3. API Endpoints

```
POST   /api/triagem/criar/                    # Iniciar nova triagem
POST   /api/triagem/{id}/responder/           # Enviar respostas
POST   /api/triagem/{id}/upload-midia/        # Upload de mídia (futuro)
POST   /api/triagem/{id}/analisar/            # Processar IA
GET    /api/triagem/{id}/resultado/           # Obter resultado
GET    /api/triagem/{id}/alertas/             # Listar alertas
```

---

### MÓDULO 2: Painel Diário (`painel_diario/`)

**Objetivo**: Registro diário de comportamento para análise temporal.

#### 2.1. Modelos de Dados

```python
# painel_diario/models.py

class Crianca(models.Model):
    """
    Perfil da criança
    """
    responsavel = models.ForeignKey('auth.User')
    nome = models.CharField(max_length=200)
    data_nascimento = models.DateField()
    genero = models.CharField(choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    diagnostico_confirmado = models.BooleanField(default=False)
    data_diagnostico = models.DateField(null=True)
    terapias_atuais = models.ManyToManyField('TipoTerapia')
    foto_perfil = models.ImageField(upload_to='criancas/', null=True)

class RegistroDiario(models.Model):
    """
    Registro diário completo
    """
    crianca = models.ForeignKey(Crianca)
    data = models.DateField()
    humor = models.CharField(choices=[
        ('muito_feliz', 'Muito Feliz 😊'),
        ('feliz', 'Feliz 🙂'),
        ('neutro', 'Neutro 😐'),
        ('triste', 'Triste ☹️'),
        ('muito_triste', 'Muito Triste 😢'),
        ('irritado', 'Irritado 😠'),
    ])
    qualidade_sono = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5
    horas_sono = models.DecimalField(max_digits=4, decimal_places=1)
    alimentacao_qualidade = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    alimentacao_observacoes = models.TextField(blank=True)
    
    # Comportamentos
    movimentos_repetitivos = models.BooleanField(default=False)
    descricao_movimentos = models.TextField(blank=True)
    contato_visual = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    resposta_ao_nome = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    interacao_social = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    
    # Comunicação
    palavras_novas = models.IntegerField(default=0)
    frases_novas = models.TextField(blank=True)
    ecolalia_presente = models.BooleanField(default=False)
    
    # Crises
    teve_crise = models.BooleanField(default=False)
    tipo_crise = models.CharField(choices=[
        ('meltdown', 'Meltdown'),
        ('shutdown', 'Shutdown'),
        ('ambos', 'Ambos'),
    ], blank=True)
    gatilho_crise = models.TextField(blank=True)
    duracao_crise = models.IntegerField(null=True, help_text="Minutos")
    
    # Terapias
    teve_terapia = models.BooleanField(default=False)
    evolucao_terapia = models.TextField(blank=True)
    
    # Observações gerais
    observacoes_livres = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

class MidiaRegistroDiario(models.Model):
    """
    Mídias anexadas ao registro diário
    """
    registro = models.ForeignKey(RegistroDiario)
    tipo = models.CharField(choices=[
        ('foto', 'Foto'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
    ])
    arquivo = models.FileField(upload_to='registros/%Y/%m/%d/')
    descricao = models.CharField(max_length=255, blank=True)
    data_upload = models.DateTimeField(auto_now_add=True)

class TipoTerapia(models.Model):
    """
    Tipos de terapia disponíveis
    """
    nome = models.CharField(max_length=100)  # "ABA", "Fonoaudiologia", "TO", etc.
    descricao = models.TextField()
    
class SessaoTerapia(models.Model):
    """
    Registro de sessões de terapia
    """
    crianca = models.ForeignKey(Crianca)
    tipo_terapia = models.ForeignKey(TipoTerapia)
    data = models.DateField()
    duracao = models.IntegerField(help_text="Minutos")
    profissional = models.CharField(max_length=200)
    objetivos_trabalhados = models.TextField()
    evolucao = models.TextField()
    proximos_passos = models.TextField(blank=True)
```

#### 2.2. Funcionalidades

- ✅ Registro diário de humor, sono, alimentação
- ✅ Rastreamento de comportamentos repetitivos
- ✅ Avaliação de interação social
- ✅ Registro de crises (meltdowns/shutdowns)
- ✅ Evolução de terapias
- ✅ Upload de fotos/vídeos/áudios
- ✅ Gráficos de evolução temporal
- ✅ Comparação entre períodos
- ✅ Alertas de regressão (IA)

#### 2.3. API Endpoints

```
POST   /api/painel/registro-diario/           # Criar registro
GET    /api/painel/registro-diario/           # Listar registros (com filtros)
PUT    /api/painel/registro-diario/{id}/      # Editar registro
GET    /api/painel/evolucao/                   # Gráficos de evolução
GET    /api/painel/alertas/                    # Alertas da IA
POST   /api/painel/sessao-terapia/            # Registrar terapia
```

---

### MÓDULO 3: Comunidade (`comunidade/`)

**Objetivo**: Rede social segura para pais compartilharem experiências.

#### 3.1. Modelos de Dados

```python
# comunidade/models.py

class PerfilPai(models.Model):
    """
    Perfil do usuário na comunidade
    """
    usuario = models.OneToOneField('auth.User')
    nome_exibicao = models.CharField(max_length=100)
    bio = models.TextField(max_length=500, blank=True)
    foto_perfil = models.ImageField(upload_to='perfis/', null=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    compartilhar_evolucao = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

class Grupo(models.Model):
    """
    Grupos temáticos da comunidade
    """
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    criador = models.ForeignKey('auth.User')
    membros = models.ManyToManyField('auth.User', through='MembroGrupo')
    tipo = models.CharField(choices=[
        ('idade', 'Faixa Etária'),
        ('terapia', 'Tipo de Terapia'),
        ('regiao', 'Região Geográfica'),
        ('geral', 'Geral'),
    ])
    privado = models.BooleanField(default=False)
    moderadores = models.ManyToManyField('auth.User', related_name='grupos_moderados')
    data_criacao = models.DateTimeField(auto_now_add=True)

class MembroGrupo(models.Model):
    """
    Relacionamento de membros em grupos
    """
    usuario = models.ForeignKey('auth.User')
    grupo = models.ForeignKey(Grupo)
    data_entrada = models.DateTimeField(auto_now_add=True)
    notificacoes_ativas = models.BooleanField(default=True)

class Postagem(models.Model):
    """
    Postagens na comunidade
    """
    autor = models.ForeignKey('auth.User')
    grupo = models.ForeignKey(Grupo, null=True)  # Null = feed público
    titulo = models.CharField(max_length=255, blank=True)
    conteudo = models.TextField()
    tipo = models.CharField(choices=[
        ('relato', 'Relato'),
        ('duvida', 'Dúvida'),
        ('conquista', 'Conquista'),
        ('desabafo', 'Desabafo'),
        ('recurso', 'Compartilhamento de Recurso'),
    ])
    anexo = models.FileField(upload_to='comunidade/postagens/', null=True)
    visibilidade = models.CharField(choices=[
        ('publico', 'Público'),
        ('amigos', 'Apenas Amigos'),
        ('grupo', 'Apenas Grupo'),
    ])
    moderado = models.BooleanField(default=True)  # False = aguarda moderação
    data_publicacao = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(null=True)

class Comentario(models.Model):
    """
    Comentários em postagens
    """
    postagem = models.ForeignKey(Postagem)
    autor = models.ForeignKey('auth.User')
    conteudo = models.TextField()
    moderado = models.BooleanField(default=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)

class ReacaoPostagem(models.Model):
    """
    Reações às postagens (like, apoio, etc.)
    """
    postagem = models.ForeignKey(Postagem)
    usuario = models.ForeignKey('auth.User')
    tipo_reacao = models.CharField(choices=[
        ('apoio', '❤️ Apoio'),
        ('obrigado', '🙏 Obrigado'),
        ('forca', '💪 Força'),
        ('celebracao', '🎉 Parabéns'),
    ])
    data_reacao = models.DateTimeField(auto_now_add=True)

class ConteudoProfissional(models.Model):
    """
    Conteúdos criados por profissionais verificados
    """
    autor = models.ForeignKey('auth.User')  # Deve ter permissão 'profissional_verificado'
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField()
    categoria = models.CharField(choices=[
        ('orientacao', 'Orientação'),
        ('exercicio', 'Exercício'),
        ('dica', 'Dica'),
        ('artigo', 'Artigo'),
    ])
    tags = models.ManyToManyField('Tag')
    arquivo_anexo = models.FileField(upload_to='profissionais/', null=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)

class Moderacao(models.Model):
    """
    Log de moderações realizadas
    """
    moderador = models.ForeignKey('auth.User')
    tipo_objeto = models.CharField(choices=[
        ('postagem', 'Postagem'),
        ('comentario', 'Comentário'),
    ])
    objeto_id = models.IntegerField()
    acao = models.CharField(choices=[
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('editado', 'Editado'),
        ('removido', 'Removido'),
    ])
    motivo = models.TextField()
    data_acao = models.DateTimeField(auto_now_add=True)
```

#### 3.2. Funcionalidades

- ✅ Feed de postagens
- ✅ Grupos temáticos
- ✅ Comentários e reações
- ✅ Sistema de moderação
- ✅ Conteúdos de profissionais verificados
- ✅ Notificações
- ✅ Busca e filtros
- ✅ Privacidade configurável

---

### MÓDULO 4: Profissionais (`profissionais/`) - **FUTURO**

**Objetivo**: Dashboard para terapeutas e profissionais de saúde.

#### 4.1. Funcionalidades Planejadas

- ⏳ Dashboard de pacientes
- ⏳ Visualização de evolução
- ⏳ Acesso a resultados de triagem (com permissão)
- ⏳ Plano Terapêutico Individual (PTI)
- ⏳ Teleatendimento
- ⏳ Notas clínicas

---

### MÓDULO 5: Biblioteca de Conteúdos (`biblioteca_conteudos/`)

**Objetivo**: Conteúdos educativos oficiais.

#### 5.1. Modelos de Dados

```python
# biblioteca_conteudos/models.py

class CategoriaConteudo(models.Model):
    """
    Categorias de conteúdo
    """
    nome = models.CharField(max_length=100)
    slug = models.SlugField()
    icone = models.CharField(max_length=50)  # FontAwesome ou emoji
    ordem = models.IntegerField(default=0)

class Conteudo(models.Model):
    """
    Conteúdos educativos
    """
    titulo = models.CharField(max_length=255)
    categoria = models.ForeignKey(CategoriaConteudo)
    tipo = models.CharField(choices=[
        ('artigo', 'Artigo'),
        ('video', 'Vídeo'),
        ('pdf', 'PDF'),
        ('infografico', 'Infográfico'),
        ('checklist', 'Checklist'),
    ])
    conteudo = models.TextField()
    autor = models.ForeignKey('auth.User')
    arquivo = models.FileField(upload_to='biblioteca/', null=True)
    url_externa = models.URLField(blank=True)
    tags = models.ManyToManyField('Tag')
    destaque = models.BooleanField(default=False)
    visualizacoes = models.IntegerField(default=0)
    data_publicacao = models.DateTimeField(auto_now_add=True)
```

---

### MÓDULO 6: CMS Wagtail

**Objetivo**: Gerenciamento de conteúdo público institucional.

#### 6.1. Páginas Wagtail

- ✅ **HomePage**: Página inicial com destaques
- ✅ **NoticiaIndexPage**: Listagem de notícias
- ✅ **NoticiaPage**: Página de notícia individual
- ✅ **ArtigoPage**: Artigos científicos/educativos
- ✅ **BibliotecaPage**: Biblioteca de recursos
- ✅ **SobrePage**: Sobre o projeto
- ✅ **ContatoPage**: Formulário de contato
- ✅ **PoliticasPage**: Termos de uso, privacidade, LGPD

#### 6.2. Blocos Reutilizáveis (mantidos do projeto anterior)

- ✅ TituloBlock
- ✅ BannerComLinkBlock
- ✅ CarrosselBannersBlock
- ✅ NoticiasListBlock
- ✅ ListaVideosBlock
- ✅ GridImagensBlock
- ✅ LinhaDoTempoBlock
- ✅ AcordeonBlock
- ✅ CustomFormBlock
- ✅ RedesSociaisBlock

---

## 🔄 Fluxo de Dados

### Fluxo 1: Triagem Completa

```
Pai/Responsável
    │
    ├─► Preenche questionários (M-CHAT-R, Q-CHAT)
    │
    ├─► Escreve relatos livres
    │
    ├─► [FUTURO] Faz upload de foto/vídeo/áudio
    │
    ▼
Sistema Backend (Django)
    │
    ├─► Salva respostas no banco (PostgreSQL)
    │
    ├─► Envia para fila de processamento (Celery)
    │
    ▼
Módulo IA (Multimodal)
    │
    ├─► Analisa texto (NLP)
    │
    ├─► [FUTURO] Analisa imagem/vídeo (Computer Vision)
    │
    ├─► [FUTURO] Analisa áudio (Speech Analysis)
    │
    ├─► Fusão Multimodal (Ensemble Model)
    │
    ├─► Calcula probabilidade de risco
    │
    ├─► Gera recomendações personalizadas
    │
    ▼
Sistema Backend
    │
    ├─► Salva ResultadoIA no banco
    │
    ├─► Cria AlertaIA se necessário
    │
    ├─► Envia notificação ao responsável
    │
    ▼
Pai/Responsável
    │
    └─► Visualiza resultado e recomendações
```

### Fluxo 2: Registro Diário + Análise Temporal

```
Pai/Responsável
    │
    ├─► Registra humor, sono, alimentação (diariamente)
    │
    ├─► Registra comportamentos e interações
    │
    ├─► [Opcional] Upload de mídia
    │
    ▼
Sistema Backend
    │
    ├─► Salva RegistroDiario
    │
    ├─► A cada 7 dias → Analisa tendências (Celery Task)
    │
    ▼
Módulo IA (Análise Temporal)
    │
    ├─► Compara com semana anterior
    │
    ├─► Detecta padrões (regressão/avanço)
    │
    ├─► Gera AlertaIA se detectar regressão
    │
    ▼
Pai/Responsável
    │
    ├─► Recebe alerta (se houver)
    │
    └─► Visualiza gráficos de evolução
```

---

## 🔒 Segurança e LGPD

### Conformidade LGPD

O sistema **lida com dados sensíveis de saúde de crianças**, portanto segue **LGPD (Lei Geral de Proteção de Dados)** rigorosamente:

#### 7.1. Medidas Implementadas

✅ **Consentimento Explícito**
- Termo de consentimento obrigatório no cadastro
- Opção de revogação de consentimento a qualquer momento

✅ **Minimização de Dados**
- Coletar apenas dados essenciais para triagem

✅ **Criptografia**
- Dados sensíveis criptografados em repouso (banco de dados)
- TLS/SSL em todas as comunicações (HTTPS)

✅ **Anonimização para Pesquisa**
- Dados usados em pesquisa são completamente anonimizados
- Remoção de identificadores diretos e indiretos

✅ **Direitos do Titular**
- **Acesso**: Visualizar todos os dados coletados
- **Retificação**: Editar dados incorretos
- **Exclusão**: Deletar conta e todos os dados (right to be forgotten)
- **Portabilidade**: Exportar dados em formato legível (JSON/CSV)

✅ **Segurança de Acesso**
- Autenticação obrigatória
- Senhas com hash bcrypt
- Sessões seguras
- Rate limiting em APIs
- CAPTCHA em formulários sensíveis

✅ **Logs de Auditoria**
- Registrar quem acessou quais dados e quando
- Logs imutáveis

#### 7.2. Modelos de Dados para LGPD

```python
# core/models.py

class ConsentimentoLGPD(models.Model):
    """
    Registro de consentimento do usuário
    """
    usuario = models.OneToOneField('auth.User')
    aceite_coleta_dados = models.BooleanField(default=False)
    aceite_analise_ia = models.BooleanField(default=False)
    aceite_pesquisa_anonima = models.BooleanField(default=False)
    aceite_compartilhamento_profissionais = models.BooleanField(default=False)
    data_aceite = models.DateTimeField(auto_now_add=True)
    data_revogacao = models.DateTimeField(null=True)
    ip_aceite = models.GenericIPAddressField()

class LogAcesso(models.Model):
    """
    Log de acessos a dados sensíveis
    """
    usuario = models.ForeignKey('auth.User')
    acao = models.CharField(max_length=100)  # "visualizou_resultado", "exportou_dados"
    tabela_acessada = models.CharField(max_length=100)
    objeto_id = models.IntegerField()
    ip = models.GenericIPAddressField()
    data_hora = models.DateTimeField(auto_now_add=True)

class SolicitacaoExclusao(models.Model):
    """
    Solicitações de exclusão de dados (Right to be Forgotten)
    """
    usuario = models.ForeignKey('auth.User')
    motivo = models.TextField()
    status = models.CharField(choices=[
        ('pendente', 'Pendente'),
        ('em_processamento', 'Em Processamento'),
        ('concluida', 'Concluída'),
    ])
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True)
```

---

## 🗓️ Roadmap de Desenvolvimento

### FASE 1: MVP (3-4 meses) - TCC

✅ **Concluído:**
- [x] Estrutura Django + Wagtail
- [x] Frontend base (HTML + Sass + JS)
- [x] Build system (Webpack)
- [x] Limpeza de código governamental

⏳ **Em andamento:**
- [ ] Criação dos apps principais (triagem_ia, painel_diario, comunidade)
- [ ] Modelos de dados completos
- [ ] Sistema de autenticação customizado
- [ ] Questionários M-CHAT-R e Q-CHAT
- [ ] Registro diário básico
- [ ] Análise de texto com IA (NLP básico)
- [ ] Cálculo de risco inicial (baseado em regras)
- [ ] Interface de usuário básica
- [ ] Gráficos de evolução
- [ ] Conformidade LGPD

**Entregáveis MVP:**
- ✅ Sistema funcional de triagem por questionário
- ✅ Painel diário básico
- ✅ Resultado de análise com IA (texto)
- ✅ Gráficos de evolução
- ✅ CMS público funcional
- ✅ Documentação completa

---

### FASE 2: Multimodalidade (6-9 meses) - Pós-TCC

- [ ] Módulo de Computer Vision (análise de fotos/vídeos)
- [ ] Módulo de Speech Analysis (análise de áudio)
- [ ] Fusão multimodal (ensemble)
- [ ] Treinamento de modelos com datasets públicos
- [ ] Refinamento da IA com feedback real
- [ ] Comunidade completa (grupos, postagens, moderação)
- [ ] Sistema de notificações push
- [ ] App mobile (React Native ou Flutter)

---

### FASE 3: Profissionalização (12+ meses)

- [ ] Dashboard para profissionais
- [ ] Teleatendimento
- [ ] Planos de assinatura
- [ ] API pública para integrações
- [ ] Expansão para outros transtornos do neurodesenvolvimento
- [ ] Certificação de segurança (ISO 27001)
- [ ] Parcerias com clínicas e universidades

---

## 📚 Referências Científicas

1. **Thabtah, F.** (2017). "Machine learning in autistic spectrum disorder behavioral research: A review and ways forward." *Informatics for Health and Social Care*.

2. **Duda, M., et al.** (2016). "Use of machine learning for behavioral distinction of autism and ADHD." *Translational Psychiatry*.

3. **Bone, D., et al.** (2016). "Applying machine learning to facilitate autism diagnostics: Pitfalls and promises." *Journal of Autism and Developmental Disorders*.

4. **Multimodal Fusion Research** - Pesquisa base do projeto.

---

## 🛠️ Ferramentas de Desenvolvimento

- **IDE**: VS Code com Pylance
- **Controle de Versão**: Git + GitLab/GitHub
- **CI/CD**: GitLab CI ou GitHub Actions
- **Testes**: pytest + coverage
- **Linting**: flake8, black, isort
- **Documentação**: Sphinx ou MkDocs

---

## 📧 Contato

**Desenvolvedor**: [Seu Nome]  
**Email**: [Seu Email]  
**GitHub**: [Seu GitHub]  
**Universidade**: [Sua Universidade]

---

*Última atualização: 24/11/2025*
