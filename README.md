# NeuroPrev Multimodal

## Sistema de Triagem Precoce de Autismo com IA Multimodal

Plataforma completa baseada em pesquisa científica para triagem precoce de Transtorno do Espectro Autista (TEA), integrando análise multimodal (texto, imagem, vídeo, áudio) e um ecossistema de suporte para pais e profissionais.

---

## 🎯 Sobre o Projeto

O **NeuroPrev Multimodal** é um sistema desenvolvido como TCC e projeto profissional, baseado na pesquisa *"A multimodular approach to streamline autism diagnosis in young children"*. O sistema oferece:

- **Triagem Multimodal de Autismo** - Análise integrada de 4 modalidades (texto, imagem, vídeo, áudio)
- **Painel Diário para Responsáveis** - Registro completo do desenvolvimento da criança
- **Comunidade para Pais** - Espaço seguro para compartilhamento e suporte
- **Área para Profissionais** - Dashboard clínico e teleatendimento (futuro)
- **CMS Educativo** - Conteúdo confiável gerenciado via Wagtail

### Stack Tecnológica

- **Backend**: Django 5.1.x + Wagtail 7.x (Python 3.12+)
- **Frontend**: JavaScript/Webpack (ES6+, Babel, Jest)
- **IA**: Modelos multimodais (em desenvolvimento)
- **Banco de Dados**: PostgreSQL (produção), SQLite (desenvolvimento/testes)
- **Segurança**: LGPD-compliant, criptografia de dados sensíveis

### Módulos Principais

- `triagem/` - Core da triagem multimodal com IA
- `painel_diario/` - Registro diário de desenvolvimento
- `comunidade/` - Rede social para pais
- `profissionais/` - Dashboard para terapeutas
- `conteudo_educativo/` - CMS Wagtail para artigos
- `noticias/` - Blog e atualizações
- `lgpd/` - Conformidade com proteção de dados
- `api/` - REST API para integrações
- `core/` - Configurações e utilitários centrais
- `blocks/` - Blocos Wagtail reutilizáveis

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades-do-sistema)
- [Arquitetura](#-arquitetura-do-sistema)
- [Instalação](#-instalação)
  - [Setup com Docker](#setup-com-docker)
  - [Setup com Virtualenv](#setup-com-virtualenv)
- [Desenvolvimento](#-desenvolvimento)
- [Testes](#-testes)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)

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

---

### MÓDULO 2 — Painel Diário para Pais

Sistema completo de registro usado também na análise temporal pela IA.

#### 2.1. Entradas Diárias

- ✅ Humor da criança
- ✅ Qualidade do sono
- ✅ Alimentação
- ✅ Comportamentos repetitivos
- ✅ Interações sociais
- ✅ Responsividade
- ✅ Sessões de terapia e evolução
- ✅ Crises / gatilhos
- ✅ Observações livres
- ✅ Upload diário de foto/vídeo (opcional)
- ✅ Gravação de áudio espontâneo

#### 2.2. Histórico e Análises

- ✅ Linha do tempo completa
- ✅ Gráficos de evolução
- ✅ Comparação entre semanas
- ✅ Alertas automáticos gerados pela IA

---

### MÓDULO 3 — IA Multimodal

#### 3.1. Modalidades Integradas

1. **Texto** - Respostas de questionários e relatos
2. **Imagem** - Análise de expressões e comportamentos visuais
3. **Vídeo** - Detecção de padrões comportamentais
4. **Áudio** - Análise prosódica e vocal
5. **Temporal** - Progressão ao longo do tempo

#### 3.2. Funcionalidades

- ✅ Detecção de sinais precoces
- ✅ Fusão multimodal para precisão elevada
- ✅ Risco estimado probabilístico
- ✅ Recomendações personalizadas
- ✅ Alertas de regressão
- ✅ Indicadores de progresso terapêutico

---

### MÓDULO 4 — Comunidade para Pais

Espaço seguro e moderado para troca de experiências.

#### Funcionalidades:

- ✅ Perfis de pais
- ✅ Postagens, relatos, dúvidas
- ✅ Comentários e interações
- ✅ Grupos fechados (por idade, terapias, regiões)
- ✅ Compartilhamento de evolução
- ✅ Biblioteca de conteúdos oficiais de profissionais

---

### MÓDULO 5 — Profissionais e Terapeutas (Futuro)

Para versão comercial:

- ✅ Dashboard para terapeutas
- ✅ Compartilhamento de evolução clínica
- ✅ Teleatendimento
- ✅ Plano terapêutico individual (PTI)
- ✅ Monitoramento remoto

---

### MÓDULO 6 — CMS Wagtail para Conteúdo Educativo

Sistema de gerenciamento de conteúdo para:

- ✅ Páginas de notícias e artigos
- ✅ Avisos e atualizações
- ✅ Páginas institucionais (Sobre, Contato, Políticas)
- ✅ Blog com orientações profissionais
- ✅ Gerenciamento de banners
- ✅ Conteúdo sem dependência de código

---

## 🏗️ Arquitetura do Sistema

```
NeuroPrev Multimodal/
│
├── Backend (Django + Wagtail)
│   ├── triagem/              # Core - Análise multimodal
│   ├── painel_diario/         # Registro diário
│   ├── comunidade/            # Rede social pais
│   ├── profissionais/         # Dashboard terapeutas
│   ├── conteudo_educativo/    # CMS Wagtail
│   ├── noticias/              # Blog/notícias
│   ├── lgpd/                  # Conformidade LGPD
│   ├── api/                   # REST API
│   ├── core/                  # Utilitários
│   └── blocks/                # Blocos reutilizáveis
│
├── Frontend (Webpack + Sass + JS)
│   ├── js/                    # JavaScript modular
│   ├── scss/                  # Estilos SCSS
│   └── img/                   # Imagens e assets
│
├── IA (Em desenvolvimento)
│   ├── modelos/               # Modelos treinados
│   ├── preprocessing/         # Pré-processamento
│   └── fusion/                # Fusão multimodal
│
└── Infraestrutura
    ├── PostgreSQL             # Banco de dados
    ├── Redis                  # Cache e filas
    └── Docker                 # Containerização

```

---

## 🔐 Segurança e LGPD

- ✅ Criptografia de dados sensíveis
- ✅ Conformidade com LGPD
- ✅ Autenticação segura
- ✅ Logs de auditoria
- ✅ Consentimento explícito
- ✅ Direito ao esquecimento
- ✅ Portabilidade de dados

---

# Instalação

Escolha o método de instalação que preferir:

- [Setup com Docker](#setup-com-docker) - Recomendado para começar rapidamente
- [Setup com Virtualenv](#setup-com-virtualenv) - Para desenvolvimento local tradicional

## Setup com Docker

### Dependências

- [Docker](https://docs.docker.com/engine/installation/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Instalação

Execute os seguintes comandos:

```bash
git clone <url-do-repositorio>
cd site-padrao
docker compose up --build -d
```

Após o comando completar, aguarde cerca de 10 segundos para o setup do banco de dados. Então execute:

```bash
docker compose run app /venv/bin/python manage.py migrate
docker compose run app /venv/bin/python manage.py createsuperuser
```

Se falhar com erro de banco de dados, aguarde mais 10 segundos e tente novamente. Finalmente, execute:

```bash
docker compose up
```

O site estará acessível em [http://localhost:8000/](http://localhost:8000/) e a interface admin do Wagtail em [http://localhost:8000/admin/](http://localhost:8000/admin/).

**Importante:** Este `docker-compose.yml` é configurado para testes locais apenas, e _não_ é destinado para uso em produção.

### Debugging

Para acompanhar os logs dos containers Docker em tempo real, execute:

```bash
docker compose logs -f
```

## Setup com Virtualenv

Você pode executar o projeto localmente sem Docker usando Virtualenv, que é a [abordagem de instalação recomendada](https://docs.djangoproject.com/en/stable/topics/install/#install-the-django-code) para o próprio Django.

### Dependências

- Python 3.12+
- Node.js v22.13.1+
- PostgreSQL (produção) ou SQLite (desenvolvimento)
- [Virtualenv](https://virtualenv.pypa.io/en/stable/installation.html)
- [VirtualenvWrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) (opcional)

#### Gerenciamento de Ambiente Python

Você pode usar diferentes ferramentas para gerenciar ambientes Python:
- [Virtualenv](https://virtualenv.pypa.io/en/stable/installation.html) + [VirtualenvWrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) (recomendado)
- [Conda](https://docs.conda.io/en/latest/)
- [Pyenv](https://github.com/pyenv/pyenv) com [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- [Poetry](https://python-poetry.org/)

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
cd site-padrao
nvm use
```

E o NVM automaticamente usará a versão correta do Node.js especificada no arquivo.

**Alternativa Recomendada: asdf (Gerenciador Universal de Versões)**

O [asdf](https://asdf-vm.com/) é um gerenciador de versões universal que permite gerenciar Python, Node.js e outras linguagens com uma única ferramenta.

**Instalação do asdf (Linux/macOS):**

```bash
# Clone o repositório do asdf
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0

# Adicione ao seu shell (escolha um)
# Para bash:
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
# Para zsh:
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.zshrc
echo 'fpath=(${ASDF_DIR}/completions $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc

# Recarregue o shell
source ~/.bashrc  # ou ~/.zshrc

# Verifique a instalação
asdf --version
```

**Instalação dos plugins e versões:**

```bash
# Adicione os plugins necessários
asdf plugin add python
asdf plugin add nodejs

# Instale as versões específicas do projeto
asdf install python 3.12.0
asdf install nodejs 22.13.1

# Defina as versões globalmente (opcional)
asdf global python 3.12.0
asdf global nodejs 22.13.1

# Ou use as versões definidas no arquivo .tool-versions do projeto
cd site-padrao
asdf install  # Instala todas as versões do .tool-versions

# Verifique as versões ativas
python --version
node --version
```

**Dica:** O projeto contém um arquivo `.tool-versions` na raiz. Ao entrar na pasta do projeto após instalar o asdf, as versões corretas serão automaticamente ativadas!

**Outras Alternativas:**

- **Instalação direta do Node.js:** Baixe do [site oficial](https://nodejs.org/) (menos flexível para múltiplas versões)
- **n (Node version manager):** Alternativa mais simples ao NVM
  ```bash
  npm install -g n
  n 22.13.1
  ```

### Instalação

#### Opção 1: Usando asdf (Recomendado para gerenciar Python + Node.js)

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd site-padrao

# O asdf lerá o arquivo .tool-versions e ativará as versões corretas automaticamente
# Se ainda não instalou as versões, execute:
asdf install

# Verifique as versões
python --version  # Deve ser 3.12.0
node --version    # Deve ser v22.13.1

# Instale as dependências backend
pip install -r requirements.txt

# Instale as dependências frontend
npm install

# Configure o arquivo de ambiente (se necessário)
cp .env.example .env
# Edite .env com suas configurações

# Execute as migrations
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# (OPCIONAL) Popule o site com dados de demonstração
python manage.py populate_site
# Para limpar dados anteriores e repopular:
# python manage.py populate_site --clear

# Build do frontend
npm run build

# Inicie o servidor de desenvolvimento
python manage.py runserver
```

### Dados de Demonstração

O projeto inclui um comando Django para popular o site com dados de demonstração, útil para desenvolvimento e testes.

**O que é criado:**
- 2 usuários de teste (admin e editor)
- 5 categorias de notícias
- 5 imagens de demonstração (coloridas)
- Estrutura de páginas (HomePage, NoticiasIndexPages)
- 10 notícias com categorias e imagens

**Comando:**
```bash
# Popular com dados de demonstração
python manage.py populate_site

# Limpar dados existentes e repopular
python manage.py populate_site --clear
```

**Credenciais criadas:**
- **Admin**: `admin` / `admin123` (superuser)
- **Editor**: `editor` / `editor123` (staff, grupo Editores)

**⚠️ Importante:** Use `--clear` com cuidado, pois remove usuários `admin` e `editor`, todas as categorias e imagens de demonstração criadas anteriormente.

#### Opção 2: Usando Virtualenv + NVM (Tradicional)

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd site-padrao

# Configure o ambiente Python (escolha uma opção)
# Opção A: virtualenvwrapper
mkvirtualenv sitepadrao
# Opção B: venv nativo
python -m venv venv && source venv/bin/activate
# Opção C: conda
conda create -n sitepadrao python=3.12 && conda activate sitepadrao
# Opção D: pyenv
pyenv virtualenv 3.12.0 sitepadrao && pyenv activate sitepadrao

# Verifique a versão do Python
python --version  # Deve ser 3.12+

# Configure Node.js (escolha uma opção)
# Opção A: NVM (usa a versão do .nvmrc automaticamente)
nvm use
# Opção B: NVM com versão específica
nvm use 22.13.1
# Opção C: Se instalou Node.js globalmente
node --version  # Verifique se é 22.x

# Instale as dependências backend
pip install -r requirements.txt

# Instale as dependências frontend
npm install

# Configure o arquivo de ambiente (se necessário)
cp .env.example .env
# Edite .env com suas configurações

# Execute as migrations
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Build do frontend
npm run build

# Inicie o servidor de desenvolvimento
python manage.py runserver
```

O site estará acessível em [http://localhost:8000/](http://localhost:8000/) e a interface admin em [http://localhost:8000/admin/](http://localhost:8000/admin/).

### 7. Compile os assets do frontend

```bash
npm run build
```

### 8. Execute o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse:
- Site: [http://localhost:8000/](http://localhost:8000/)
- Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)


# GitHub Copilot Configuration

Este projeto está configurado para funcionar com GitHub Copilot e outras ferramentas de IA. As configurações estão em `.github/copilot-instructions.md` e incluem:

- Padrões de código DRY (Don't Repeat Yourself)
- Boas práticas de testes
- Padrões Wagtail específicos
- Problemas comuns e soluções
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
workon sitepadrao
# ou: source venv/bin/activate
# ou: conda activate sitepadrao
# ou: pyenv activate sitepadrao
\`\`\`

### Ativar Versão do Node.js
\`\`\`bash
nvm use v22.13.1
# ou: asdf local nodejs 22.13.1
# ou: deixe em branco se usar versão global
\`\`\`

## Comando Completo para Ativar Ambiente
\`\`\`bash
workon sitepadrao && nvm use v22.13.1
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
neuroprev-multimodal/
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
└── sitepadrao/               # 🔧 Configurações Django
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

# 🤝 Contribuindo

Contribuições são bem-vindas! Este é um projeto de código aberto voltado para ajudar famílias e profissionais na identificação precoce de TEA.

## Padrão de Commits

Este projeto segue o padrão de commits semântico:

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `refactor:` refatoração de código
- `test:` adição/modificação de testes
- `docs:` documentação
- `style:` formatação, ponto e vírgula, etc
- `chore:` atualização de dependências, configurações
- `ai:` melhorias nos modelos de IA
- `security:` correções de segurança

Exemplo:
```bash
git commit -m "feat: adiciona análise multimodal de vídeo

- Implementa detecção de contato visual
- Adiciona análise de resposta ao nome
- Integra com modelo de fusão multimodal
- Adiciona testes unitários e de integração
- Atualiza documentação da API"
```

## Checklist para Pull Requests

- [ ] Código segue princípios DRY (Don't Repeat Yourself)
- [ ] Testes criados e passando (mínimo 70% coverage)
- [ ] Migrations criadas e aplicadas
- [ ] `python manage.py check` sem erros
- [ ] `npm run lint` sem erros
- [ ] Commits seguem padrão semântico
- [ ] Documentação atualizada se necessário
- [ ] Dados sensíveis protegidos (LGPD)
- [ ] Acessibilidade verificada (WCAG 2.1 AA)

# Configurações

## Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
# ou use SQLite para desenvolvimento:
# DATABASE_URL=sqlite:///db.sqlite3

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Configurações de Testes

Os testes usam configurações específicas em `sitepadrao/settings/testing.py`:

- Banco de dados: SQLite in-memory
- Email: Console backend
- Debug: False
- Locale padrão: pt (normalizado de pt-br)

---

# 📚 Recursos

## Documentação Técnica

- [Documentação oficial do Wagtail](https://docs.wagtail.org/)
- [Documentação do Django](https://docs.djangoproject.com/)
- [Configuração do GitHub Copilot](.github/copilot-instructions.md)
- [REST Framework](https://www.django-rest-framework.org/)

## Pesquisa e Referências

- Pesquisa base: *"A multimodular approach to streamline autism diagnosis in young children"*
- [M-CHAT - Modified Checklist for Autism in Toddlers](https://mchatscreen.com/)
- [Q-CHAT - Quantitative Checklist for Autism in Toddlers](https://www.autismresearchcentre.com/)
- [CDC - Autism Spectrum Disorder](https://www.cdc.gov/ncbddd/autism/index.html)
- [LGPD - Lei Geral de Proteção de Dados](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)

## Comunidade

- **Issues**: Reporte bugs ou sugira funcionalidades
- **Discussions**: Participe de discussões sobre o projeto
- **Pull Requests**: Contribua com código

---

# 📄 Licença

Este projeto é desenvolvido como TCC e projeto profissional, com objetivo de apoio à identificação precoce de TEA.

**Importante**: Este sistema é uma ferramenta de **triagem** e **não substitui** avaliação profissional completa. Sempre consulte profissionais de saúde especializados.

---

# 👥 Autores e Contato

- **Desenvolvedor**: [Seu Nome]
- **TCC**: [Instituição]
- **Orientador**: [Nome do Orientador]

---

# 🙏 Agradecimentos

- Famílias que compartilham suas experiências
- Profissionais de saúde especializados em TEA
- Comunidade open-source
- Pesquisadores da área de IA aplicada à saúde

---

**⚠️ Aviso Legal**: O NeuroPrev Multimodal é uma ferramenta de triagem baseada em pesquisa científica e não substitui diagnóstico médico profissional. Sempre busque avaliação de profissionais especializados em Transtorno do Espectro Autista.

---

**🌟 Se este projeto está ajudando você, considere dar uma estrela no repositório!**

# atividade-A3-Pablo