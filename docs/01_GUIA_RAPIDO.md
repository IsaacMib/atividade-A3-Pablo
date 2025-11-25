# 🚀 Guia Rápido - NEUROATHENA

Instruções para configurar e executar o projeto NEUROATHENA localmente.

---

## 📋 Pré-requisitos

- **Python**: 3.12+ (recomendado 3.14.0)
- **Node.js**: 16+ (para build do frontend)
- **PostgreSQL**: 12+ (produção) ou SQLite (desenvolvimento)
- **Redis**: Para cache e Celery (opcional em dev)
- **Git**: Para controle de versão

---

## 🛠️ Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/neuroathena.git
cd neuroathena
```

### 2. Crie o Ambiente Virtual

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instale as Dependências JavaScript

```bash
npm install
npm run build
```

### 5. Configure Variáveis de Ambiente

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite `.env` com suas configurações locais (banco de dados, SECRET_KEY, etc.)

### 6. Execute as Migrations

```bash
python manage.py migrate
```

### 7. Crie um Superusuário

```bash
python manage.py createsuperuser
```

### 8. Execute o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse: **http://localhost:8000**  
Admin Wagtail: **http://localhost:8000/admin**

---

## 🏗️ Estrutura do Projeto

```
neuroathena/
├── core/              # Configurações e modelos base
├── home/              # Páginas institucionais
├── blocks/            # Blocos Wagtail reutilizáveis
├── noticias/          # Sistema de notícias
├── triagem_ia/        # Sistema de triagem TEA
├── painel_diario/     # Painel diário das famílias
├── profissionais/     # Dashboard profissionais
├── comunidade/        # Recursos comunitários
├── lgpd/              # Compliance e privacidade
├── athena-ai/         # IA Multimodal (FastAPI)
├── frontend/          # JavaScript e SCSS
└── docs/              # Documentação
```

---

## 🎯 Páginas Institucionais Disponíveis

Após rodar migrations, você pode criar estas páginas no admin do Wagtail:

1. **HomePage** - Página inicial principal
2. **SobreNosPage** - Sobre o LUMIPSYCHE e NEUROATHENA
3. **ParaFamiliasPage** - Informações para pais e cuidadores
4. **ParaProfissionaisPage** - Recursos para profissionais
5. **IAMultimodalPage** - Explicação da IA Athena
6. **ContatoPage** - Formulário de contato

---

## 🧩 Blocos Disponíveis (StreamField)

Os seguintes blocos podem ser usados nas páginas:

- **HeroBlock** - Seção hero com título, subtítulo e CTAs
- **FeatureCardsBlock** - Grid de cards de funcionalidades
- **TimelineBlock** - Timeline de passos/eventos
- **FAQBlock** - Seção de perguntas frequentes
- **CTASectionBlock** - Call-to-action destacado
- **TestimonialBlock** - Depoimentos de usuários
- **StatisticsBlock** - Estatísticas destacadas
- **ImageTextBlock** - Imagem com texto ao lado
- **RichTextSectionBlock** - Seção de texto rico

---

## 🔧 Comandos Úteis

```bash
# Criar novas migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Coletar arquivos estáticos (produção)
python manage.py collectstatic

# Executar testes
python manage.py test

# Build do frontend
npm run build

# Watch mode frontend (desenvolvimento)
npm run watch
```

---

## 🐳 Docker (Opcional)

```bash
# Subir serviços (PostgreSQL, Redis)
docker-compose up -d

# Parar serviços
docker-compose down
```

---

## 🤖 IA Multimodal (Athena)

Para trabalhar com a IA:

```bash
cd athena-ai
pip install -r requirements.txt
python -m api.main  # Inicia API FastAPI
```

API disponível em: **http://localhost:8001**

---

## 📚 Próximos Passos

1. Leia **[DESENVOLVIMENTO.md](./DESENVOLVIMENTO.md)** para guidelines de código
2. Consulte **[03_ARQUITETURA/estrutura_site.md](./03_ARQUITETURA/estrutura_site.md)** para estrutura completa
3. Veja **[Estrutura.md](./Estrutura.md)** para visão geral do projeto

---

## 🆘 Problemas Comuns

### Python não encontrado
- Certifique-se de que Python está no PATH
- Use `python3` em vez de `python` no Linux/Mac

### Erro de permissão no PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro ao instalar psycopg2
```bash
pip install psycopg2-binary
```

### Build do frontend falha
```bash
rm -rf node_modules package-lock.json
npm install
```

---

**Dúvidas?** Consulte a [documentação completa](./00_INDICE_MESTRE.md).
