[Figma](https://www.figma.com/design/vn4GGPjxav6O2EymXV1GLf/Portal-Edu?node-id=14-2&t=JLNz6Ic3FyZ1IXyQ-1)

# Site Padrão CODATA-PB

Sistema de gerenciamento de conteúdo (CMS) baseado em [Wagtail](https://github.com/wagtail/wagtail) para criação de portais governamentais padronizados.

## Sobre o Projeto

Este projeto foi desenvolvido para facilitar a criação e manutenção de portais institucionais do governo da Paraíba, oferecendo:

- **Backend**: Django 5.1.x + Wagtail 7.x (Python 3.12+)
- **Frontend**: JavaScript/Webpack (ES6+, Babel, Jest)
- **Banco de Dados**: PostgreSQL (produção), SQLite (desenvolvimento/testes)
- **Apps principais**:
  - `agenda/` - Agendas e eventos com suporte a recorrência
  - `noticias/` - Notícias com categorias, tags e slideshow
  - `institucional/` - Páginas institucionais
  - `blocks/` - Blocos Wagtail reutilizáveis
  - `core/` - Configurações centrais e utilitários

**Índice**

- [Instalação](#instalação)
  - [Setup com Docker](#setup-com-docker)
  - [Setup com Virtualenv](#setup-com-virtualenv)
    - [Gerenciamento de versões com asdf](#alternativa-recomendada-asdf-gerenciador-universal-de-versões)
    - [Gerenciamento de versões com NVM](#gerenciamento-de-versão-do-nodejs)
- [Configuração do GitHub Copilot](#configuração-do-github-copilot)
- [Desenvolvimento](#desenvolvimento)
- [Testes](#testes)
- [Contribuindo](#contribuindo)

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

# Build do frontend
npm run build

# Inicie o servidor de desenvolvimento
python manage.py runserver
```

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

# Desenvolvimento

## Estrutura do Projeto

```
site-padrao/
├── frontend/              # JavaScript/CSS (Webpack, Babel, Jest)
├── agenda/                # Agendas e eventos recorrentes
├── noticias/              # Notícias, categorias e tags
├── blocks/                # Blocos Wagtail reutilizáveis
├── core/                  # Configurações e utilitários
│   ├── utils.py          # Utilitários de produção
│   └── utils_test.py     # Utilitários para testes
├── home/                  # Página inicial
├── institucional/         # Páginas institucionais
└── sitepadrao/            # Configurações Django
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
npm run watch                       # Watch mode para desenvolvimento
npm test                           # Executar testes Jest

# Validação
python manage.py check             # Verificar configuração
```

# Testes

## Executando Testes

```bash
# Todos os testes
python manage.py test --keepdb

# Testes de um app específico
python manage.py test agenda --keepdb
python manage.py test noticias --keepdb

# Com coverage
coverage run --source='.' manage.py test --keepdb
coverage report
coverage html  # Gera relatório HTML
```

## Boas Práticas de Testes

- Usar `ensure_root_page()` de `core.utils_test` para setup
- Normalizar locale: `pt-br` → `pt`
- Inicializar `root.numchild = 0`
- Sempre usar `root.refresh_from_db()` após operações

Veja `.github/copilot-instructions.md` para mais detalhes.

# Contribuindo

## Padrão de Commits

Este projeto segue o padrão de commits semântico:

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `refactor:` refatoração de código
- `test:` adição/modificação de testes
- `docs:` documentação
- `style:` formatação, ponto e vírgula, etc
- `chore:` atualização de dependências, configurações

Exemplo:
```bash
git commit -m "feat: adiciona campo de recorrência em AgendaDoDiaPage

- Adiciona campos habilitar_recorrencia e tipo_recorrencia
- Cria método data_aplica_na_recorrencia()
- Adiciona testes de recorrência
- Atualiza template para exibir eventos recorrentes"
```

## Checklist para Pull Requests

- [ ] Código segue princípios DRY
- [ ] Testes criados e passando
- [ ] Migrations criadas e aplicadas
- [ ] `python manage.py check` sem erros
- [ ] Coverage mínimo de 70%
- [ ] Commits seguem padrão semântico
- [ ] Documentação atualizada se necessário

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

# Recursos

## Documentação

- [Documentação oficial do Wagtail](https://docs.wagtail.org/)
- [Documentação do Django](https://docs.djangoproject.com/)
- [Configuração do GitHub Copilot](.github/copilot-instructions.md)

## Licença

Este projeto é desenvolvido pela CODATA-PB para uso em portais governamentais da Paraíba.
