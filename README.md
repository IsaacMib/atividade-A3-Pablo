# NEUROATHENA

## Sistema de Triagem Precoce de TEA com IA Multimodal

Plataforma Django/Wagtail para triagem precoce de Transtorno do Espectro Autista (TEA), integrando análise multimodal (texto, imagem, vídeo, áudio) e ecossistema de suporte para pais e profissionais.

---

## 🎯 Sobre o Projeto

Sistema baseado na pesquisa *"A multimodular approach to streamline autism diagnosis in young children"*.

### Funcionalidades Principais

- ✅ **Triagem Multimodal** - Análise integrada de 4 modalidades (texto, imagem, vídeo, áudio)
- ✅ **Painel Diário** - Registro de desenvolvimento da criança
- 🔄 **Comunidade** - Espaço para pais (em desenvolvimento)
- 🔄 **Dashboard Profissional** - Para terapeutas (futuro)
- ✅ **CMS Educativo** - Conteúdo gerenciado via Wagtail

### Stack Tecnológica

- **Backend**: Django 5.1 + Wagtail 7.x (Python 3.12+)
- **Frontend**: JavaScript/Webpack, SCSS
- **IA**: Athena - Modelos multimodais (vídeo, áudio, texto) - `athena-ai/`
- **Banco**: PostgreSQL (prod), SQLite (dev/test)
- **Segurança**: LGPD-compliant

---

## 📋 Documentação

- **[Guia Rápido](docs/GUIA_RAPIDO.md)** - Instalação e primeiros passos
- **[Desenvolvimento](docs/DESENVOLVIMENTO.md)** - Guia para desenvolvedores
- **[Arquitetura](docs/ARQUITETURA.md)** - Estrutura do sistema
- **[SSO/Logout](docs/logout-sso-wagtail.md)** - Configuração de autenticação

---

## 📋 Estrutura de Apps

```
neuroathena/          # Configurações Django
core/                 # Models base, utilitários
home/                 # Página inicial
noticias/             # Blog/notícias
blocks/               # Blocos Wagtail reutilizáveis
triagem_ia/           # Sistema de triagem (core)
painel_diario/        # Registro de desenvolvimento
lgpd/                 # Conformidade LGPD
search/               # Busca global
frontend/             # JavaScript, SCSS, assets
athena-ai/            # Athena - Modelos de IA
```

---

## 🚀 Funcionalidades do Sistema

### MÓDULO 1 — Triagem Multimodal de Autismo (Core)

O coração do sistema, baseado em análise multimodal com IA.

#### 1.1. Entrada de Dados

**Questionários Estruturados:**
- M-CHAT / M-CHAT-R adaptado
- Q-CHAT
- Perguntas de desenvolvimento (linguagem, social, motor, sensorial)
- Histórico perinatal
- Comportamentos observados

**Relatos Livres:**
- Texto descritivo da rotina
- Observações detalhadas
- Eventos incomuns

**Análise de Imagem/Vídeo (IA Multimodal - Futuro):**
- Reconhecimento de expressões faciais
- Contato visual
- Resposta ao nome
- Imitabilidade
- Seguimento de objetos com o olhar
- Movimentos repetitivos

**Análise de Áudio:**
- Tom da voz
- Ritmo e fluência
- Ecolalia
- Diferenças prosódicas

#### 1.2. Análises Geradas pela IA

- ✅ Detecção de sinais precoces
- ✅ Fusão multimodal para elevar precisão
- ✅ Risco estimado usando modelos probabilísticos
- ✅ Recomendações personalizadas
- ✅ Alertas para comportamentos regressivos
- ✅ Sinais de avanço terapêutico
- ✅ Sinais de urgência (ex.: regressão de fala)

## ⚡ Início Rápido

```bash
# 1. Clone o repositório
git clone <repo-url>
cd atividade-A3-Pablo

# 2. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure banco
python manage.py migrate

# 5. Crie superusuário
python manage.py createsuperuser

# 6. Rode servidor
python manage.py runserver
```

Acesse: http://localhost:8000  
Admin: http://localhost:8000/admin

---

## 🧪 Testes

```bash
# Rodar todos os testes
python manage.py test

# Com coverage
coverage run --source='.' manage.py test
coverage report

# Testes específicos
python manage.py test core
python manage.py test noticias --keepdb
```

---

## 🤖 Athena - Sistema de IA (athena-ai/)

**Athena** é o sistema de IA multimodal para análise de TEA - veja [athena-ai/README.md](athena-ai/README.md):

- **Vídeo**: MediaPipe, InsightFace (expressões, contato visual)
- **Áudio**: Silero VAD, Wav2Vec2 (prosódia, fluência)
- **Texto**: BERT/BERTimbau (questionários, relatos)
- **Fusão**: CLIP, ImageBind (integração multimodal)

---

## 🛠️ Desenvolvimento

Veja [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md) para:
- Configuração do ambiente
- Padrões de código
- Estrutura de commits
- Criação de apps
- Boas práticas Django/Wagtail

---

## 🚀 Deploy

```bash
# Produção (PostgreSQL + Gunicorn)
export DJANGO_SETTINGS_MODULE=neuroathena.settings.production
python manage.py collectstatic --noinput
gunicorn neuroathena.wsgi:application

# Docker
docker-compose up -d
```

---

## 📄 Licença

MIT License - Projeto acadêmico/profissional

---

## 👥 Autores

Desenvolvido como TCC - Projeto NEUROATHENA
│   ├── profissionais/         # Dashboard terapeutas
│   ├── conteudo_educativo/    # CMS Wagtail
│   ├── noticias/              # Blog/notícias
│   ├── lgpd/                  # Conformidade LGPD
│   ├── api/                   # REST API
│   ├── core/                  # Utilitários
│   └── blocks/                # Blocos reutilizáveis


#### Instalação do Node.js

O Node.js é necessário para compilar e executar o código frontend do projeto (JavaScript, CSS, etc.).

**Opção 1: Instalação Direta**

A forma mais simples é baixar e instalar diretamente do site oficial:

**Linux (Ubuntu/Debian):**
```bash
# Usando NodeSource para versão específica
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verifique a instalação
node --version
npm --version
```

**macOS:**
```bash
# Usando Homebrew
brew install node@22

# Ou baixe o instalador do site oficial
# https://nodejs.org/
```

**Windows:**
- Baixe o instalador (.msi) do [site oficial do Node.js](https://nodejs.org/)
- Execute o instalador e siga as instruções
- Reinicie o terminal após a instalação

**Verificação da instalação:**
```bash
node --version  # Deve mostrar v22.x.x
npm --version   # Deve mostrar 10.x.x ou superior
```

**⚠️ Limitação:** A instalação direta instala apenas uma versão do Node.js. Se você precisa trabalhar com múltiplos projetos que usam versões diferentes, use um gerenciador de versões (veja abaixo).

#### Gerenciamento de Versão do Node.js

Se você trabalha com múltiplos projetos ou precisa de flexibilidade para trocar entre versões do Node.js, use um gerenciador de versões:

**Recomendado: NVM (Node Version Manager)**

O NVM permite instalar e alternar entre diferentes versões do Node.js facilmente.

**Instalação do NVM (Linux/macOS):**

```bash
# Instale o NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recarregue o shell
source ~/.bashrc  # ou ~/.zshrc se usar zsh

# Verifique a instalação
nvm --version
```

**Instalação do Node.js com NVM:**

```bash
# Instale a versão específica do projeto
nvm install 22.13.1

# Use a versão instalada
nvm use 22.13.1

# Defina como versão padrão (opcional)
nvm alias default 22.13.1

# Verifique a versão ativa
node --version  # Deve mostrar v22.13.1
npm --version
```

**Dica:** O projeto contém um arquivo `.nvmrc` na raiz. Ao entrar na pasta do projeto, você pode simplesmente executar:

```bash
cd neuroathena
nvm use
```

E o NVM automaticamente usará a versão correta do Node.js especificada no arquivo.

**Alternativa Recomendada: asdf (Gerenciador Universal de Versões)**

O [asdf](https://asdf-vm.com/) é um gerenciador de versões universal que permite gerenciar Python, Node.js e outras linguagens com uma única ferramenta.

**Instalação do asdf (Linux/macOS):**

```bash
# Clone o repositório do asdf
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0


- Fluxo de trabalho recomendado

## Configuração de Ambiente Local

Como cada desenvolvedor pode usar diferentes ferramentas de ambiente virtual (virtualenv, conda, pyenv, etc.), o projeto suporta configurações locais personalizadas.

### Criando o arquivo de configuração local

Crie o arquivo `.github/copilot-local.md` (que já está no `.gitignore`) com seus comandos de ambiente:

```markdown
# Configurações Locais do Ambiente de Desenvolvimento

## Comandos de Ambiente

### Ativar Ambiente Virtual Python
\`\`\`bash
workon neuroathena
# ou: source venv/bin/activate
# ou: conda activate neuroathena
# ou: pyenv activate neuroathena
\`\`\`

### Ativar Versão do Node.js
\`\`\`bash
nvm use v22.13.1
# ou: asdf local nodejs 22.13.1
# ou: deixe em branco se usar versão global
\`\`\`

## Comando Completo para Ativar Ambiente
\`\`\`bash
workon neuroathena && nvm use v22.13.1
\`\`\`
```

### Exemplo de uso

Quando a IA precisar executar comandos Python ou npm, ela irá:

1. Verificar se `.github/copilot-local.md` existe
2. Se existir, usar os comandos configurados
3. Se não existir, perguntar seus comandos de ambiente e criar o arquivo automaticamente

Isso garante que o projeto funcione em qualquer máquina sem hardcoded de comandos específicos.

### Configurações principais

O arquivo `.github/copilot-instructions.md` configura a IA para:

- ✅ Sempre verificar código duplicado antes de criar funções
- ✅ Criar testes para todas as novas funcionalidades
- ✅ Usar `core.utils_test.ensure_root_page()` em testes
- ✅ Seguir padrões de migrations do Wagtail
- ✅ Perguntar antes de gerar documentação
- ✅ Normalizar locales em testes (pt-br → pt)
- ✅ Usar padrão de commits semântico (feat:, fix:, refactor:, etc.)

Para mais detalhes, consulte o arquivo `.github/copilot-instructions.md`.

## 🗺️ Roadmap

### Fase 1 - MVP (Em Desenvolvimento)
- [x] Estrutura base do projeto
- [x] Models de triagem e crianças
- [ ] Sistema de questionários (M-CHAT, Q-CHAT)
- [ ] Painel diário básico
- [ ] Interface de cadastro de triagem
- [ ] Admin Django completo

### Fase 2 - IA Básica
- [ ] Integração com modelo de análise de texto
- [ ] Sistema de pontuação automatizado
- [ ] Alertas básicos de risco
- [ ] Relatórios PDF

### Fase 3 - Multimodalidade
- [ ] Upload e análise de imagens
- [ ] Upload e análise de vídeos
- [ ] Upload e análise de áudio
- [ ] Fusão multimodal

### Fase 4 - Comunidade
- [ ] Sistema de posts e comentários
- [ ] Grupos temáticos
- [ ] Moderação de conteúdo
- [ ] Biblioteca de recursos

### Fase 5 - Profissionais
- [ ] Dashboard para terapeutas
- [ ] Sistema de teleatendimento
- [ ] PTI (Plano Terapêutico Individual)
- [ ] Compartilhamento seguro de dados

### Fase 6 - Comercialização
- [ ] Sistema de pagamentos
- [ ] Planos de assinatura
- [ ] API para terceiros
- [ ] App mobile

---

# 💻 Desenvolvimento

## Estrutura do Projeto

```
neuroathena/
├── frontend/                  # JavaScript/CSS (Webpack, Babel, Jest)
│   ├── js/                   # JavaScript ES6+
│   ├── scss/                 # Sass/SCSS
│   └── img/                  # Imagens e assets
├── triagem/                  # 🧠 Core - Triagem Multimodal
│   ├── models.py            # Criança, Triagem, Questionário, Mídia
│   ├── views.py             # Views de triagem
│   └── admin.py             # Admin customizado
├── painel_diario/            # 📊 Painel Diário
├── comunidade/               # 👥 Comunidade para Pais
├── profissionais/            # 👨‍⚕️ Área Profissionais
├── conteudo_educativo/       # 📚 CMS Wagtail
├── noticias/                 # 📰 Blog/Notícias
├── lgpd/                     # 🔒 LGPD e Privacidade
├── api/                      # 🔌 REST API
├── blocks/                   # 🧱 Blocos Wagtail reutilizáveis
├── core/                     # ⚙️ Configurações e utilitários
│   ├── utils.py             # Utilitários de produção
│   └── utils_test.py        # Utilitários para testes
├── home/                     # 🏠 Página inicial
└── neuroathena/             # 🔧 Configurações Django
    └── settings/
        ├── base.py
        ├── development.py
        ├── production.py
        └── testing.py
```

## Comandos Úteis

```bash
# Desenvolvimento
python manage.py runserver          # Servidor de desenvolvimento
python manage.py makemigrations     # Criar migrations
python manage.py migrate            # Aplicar migrations
python manage.py createsuperuser    # Criar usuário admin

# Frontend
npm run build                       # Build de produção
npm run dev                         # Servidor de desenvolvimento com hot-reload
npm run watch                       # Watch mode
npm test                           # Executar testes Jest

# Validação
python manage.py check              # Verificar configuração Django
npm run lint                        # Lint JavaScript e CSS
```

---

# 🧪 Testes

## Executando Testes Python/Django

```bash
# Todos os testes
python manage.py test --keepdb

# Testes de um app específico
python manage.py test triagem --keepdb
python manage.py test painel_diario --keepdb
python manage.py test comunidade --keepdb

# Com coverage
coverage run --source='.' manage.py test --keepdb
coverage report
coverage html  # Gera relatório HTML em htmlcov/

# Testes específicos
python manage.py test triagem.test_models.CriancaTestCase --keepdb
```

## Executando Testes Frontend

```bash
# Testes Jest
npm test                    # Todos os testes
npm run test:watch          # Watch mode
npm run test:coverage       # Com coverage
```

## Boas Práticas de Testes

- Usar `ensure_root_page()` de `core.utils_test` para setup
- Normalizar locale: `pt-br` → `pt`
- Inicializar `root.numchild = 0`
- Sempre usar `root.refresh_from_db()` após operações

Veja `.github/copilot-instructions.md` para mais detalhes.

---
## 🤝 Contribuindo

Veja [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md) para:
- Padrão de commits (Conventional Commits)
- Checklist de Pull Requests
- Boas práticas de código e testes

---

## ⚠️ Aviso Legal

Este sistema é uma ferramenta de **triagem** e **não substitui** avaliação profissional completa. Sempre consulte profissionais de saúde especializados em TEA.

---

## 📚 Referências

- Pesquisa base: *"A multimodular approach to streamline autism diagnosis in young children"*
- [M-CHAT](https://mchatscreen.com/) | [Q-CHAT](https://www.autismresearchcentre.com/)
- [Wagtail Docs](https://docs.wagtail.org/) | [Django Docs](https://docs.djangoproject.com/)
- [LGPD](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)