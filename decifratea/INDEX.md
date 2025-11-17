# 📇 ÍNDICE DO PROJETO - Navegação Rápida

> **Sistema de Gestão de Estoque - Projeto A3**
> 
> Este arquivo serve como **mapa de navegação** para encontrar rapidamente o que você precisa no projeto.

---

## 🚀 COMEÇAR AQUI

### Para Iniciantes:
1. **[📖 LEIA-ME PRIMEIRO](docs/LEIA-ME-PRIMEIRO.txt)** ⭐ COMECE AQUI!
2. **[📁 ORGANIZAÇÃO.md](ORGANIZACAO.md)** - Entenda a estrutura do projeto
3. **[📘 README_NOVO.md](README_NOVO.md)** - README completo

### Para Desenvolvedores:
1. **[🎨 DESIGN_GUIDE.md](docs/DESIGN_GUIDE.md)** - Guia de design
2. **[✅ CHECKLIST.md](docs/CHECKLIST.md)** - Checklist de desenvolvimento
3. **[⚙️ CORE_APP.md](docs/CORE_APP.md)** - Documentação técnica

---

## 📂 ESTRUTURA DE PASTAS

```
📦 gestao_estoque/
│
├── 📁 docs/                    📚 TODA A DOCUMENTAÇÃO
│   ├── LEIA-ME-PRIMEIRO.txt   ⭐ Início rápido
│   ├── DESIGN_GUIDE.md        🎨 Cores, tipografia, UI
│   ├── AMBIENTE_VIRTUAL.md    🐍 Config venv
│   ├── CHECKLIST.md           ✅ Checklist dev
│   ├── CORE_APP.md            ⚙️ Doc técnica
│   ├── ORDEM_DE_EXECUCAO.md   📋 Ordem de comandos
│   └── PROJETO_REESTRUTURADO.md 📜 Histórico
│
├── 📁 templates/               📄 TEMPLATES HTML
│   ├── base.html              Base template
│   └── dashboard.html         Dashboard principal
│
├── 📁 static/                  🎨 ARQUIVOS ESTÁTICOS
│   ├── css/style.css          ✅ CSS COMPILADO (PRONTO)
│   ├── scss/style.scss        SASS source
│   ├── js/script.js           JavaScript
│   └── images/                Imagens e ícones
│
├── 📁 estoque/                 🏗️ APP PRINCIPAL
│   ├── models.py              Produto, Movimentação, Alerta
│   ├── views.py               Lógica de negócio
│   ├── admin.py               Admin Django
│   └── urls.py                Rotas
│
├── 📁 home/                    🏠 WAGTAIL CMS
│   └── models.py              Páginas CMS
│
├── 📁 core/                    ⚙️ UTILITÁRIOS
│   ├── models.py              Models compartilhados
│   └── utils.py               Funções úteis
│
├── 📁 gestaoestoque/          ⚙️ CONFIGURAÇÕES DJANGO
│   ├── settings.py            Config principais
│   └── urls.py                URLs principais
│
├── 📁 scripts/                 🔧 SCRIPTS ÚTEIS
│   ├── iniciar.bat            🚀 Iniciar projeto (Win)
│   ├── setup.ps1              Setup PowerShell
│   └── setup.sh               Setup Linux/Mac
│
├── 📁 config/                  ⚙️ ARQUIVOS DE CONFIG
│   ├── .env.example           Variáveis de ambiente
│   ├── .flake8                Linting Python
│   └── tailwind.config.js     Config Tailwind
│
├── 📁 media/                   📷 UPLOADS
├── 📁 staticfiles/            📦 STATICS COLETADOS
└── 📁 logs/                    📝 LOGS DO SISTEMA
```

---

## 🗺️ NAVEGAÇÃO POR TAREFA

### 🎨 **Quero Editar o Design**
```
➡️ Editar SASS: static/scss/style.scss
➡️ CSS direto: static/css/style.css
➡️ HTML: templates/dashboard.html
➡️ JavaScript: static/js/script.js
➡️ Guia de cores: docs/DESIGN_GUIDE.md
```

### 🏗️ **Quero Modificar o Backend**
```
➡️ Models: estoque/models.py
➡️ Views: estoque/views.py
➡️ URLs: estoque/urls.py
➡️ Admin: estoque/admin.py
➡️ Settings: gestaoestoque/settings.py
```

### 📄 **Quero Criar Nova Página**
```
1️⃣ Criar template: templates/nova_pagina.html
2️⃣ Criar view: estoque/views.py
3️⃣ Adicionar rota: estoque/urls.py
4️⃣ Testar: http://127.0.0.1:8000/nova-pagina/
```

### 📚 **Quero Ler Documentação**
```
➡️ Guia inicial: docs/LEIA-ME-PRIMEIRO.txt
➡️ Design: docs/DESIGN_GUIDE.md
➡️ Técnico: docs/CORE_APP.md
➡️ Estrutura: ORGANIZACAO.md
➡️ README completo: README_NOVO.md
```

### 🔧 **Quero Executar Scripts**
```
➡️ Windows: scripts\iniciar.bat
➡️ PowerShell: scripts\setup.ps1
➡️ Linux/Mac: scripts/setup.sh
```

---

## 📖 DOCUMENTOS IMPORTANTES

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[LEIA-ME-PRIMEIRO.txt](docs/LEIA-ME-PRIMEIRO.txt)** | ⭐ Guia de início | Primeira vez no projeto |
| **[ORGANIZACAO.md](ORGANIZACAO.md)** | 📁 Mapa do projeto | Procurando onde está algo |
| **[README_NOVO.md](README_NOVO.md)** | 📘 README completo | Visão geral do projeto |
| **[DESIGN_GUIDE.md](docs/DESIGN_GUIDE.md)** | 🎨 Guia de design | Trabalhando com UI |
| **[CHECKLIST.md](docs/CHECKLIST.md)** | ✅ Checklist | Durante desenvolvimento |
| **[CORE_APP.md](docs/CORE_APP.md)** | ⚙️ Doc técnica | Entender arquitetura |
| **[ORDEM_DE_EXECUCAO.md](docs/ORDEM_DE_EXECUCAO.md)** | 📋 Ordem comandos | Setup inicial |

---

## 🎯 LINKS RÁPIDOS (Servidor Rodando)

### URLs do Sistema:
- **Dashboard:** http://127.0.0.1:8000/estoque/
- **Admin Django:** http://127.0.0.1:8000/django-admin/
- **Admin Wagtail:** http://127.0.0.1:8000/admin/
- **Home:** http://127.0.0.1:8000/

---

## 📝 COMANDOS ESSENCIAIS

```bash
# 🚀 Iniciar servidor
python manage.py runserver

# 📊 Migrações
python manage.py makemigrations
python manage.py migrate

# 👤 Criar admin
python manage.py createsuperuser

# 🎲 Dados de teste
python manage.py criar_dados_exemplo

# 📦 Coletar statics
python manage.py collectstatic

# 🧪 Testes
python manage.py test
```

---

## 🎓 PARA CADA PERFIL

### 👨‍🎨 **Designer / Frontend**
1. Leia: [DESIGN_GUIDE.md](docs/DESIGN_GUIDE.md)
2. Edite: `static/scss/style.scss`
3. Templates: `templates/`
4. Teste: Recarregue o navegador

### 👨‍💻 **Desenvolvedor Backend**
1. Leia: [CORE_APP.md](docs/CORE_APP.md)
2. Models: `estoque/models.py`
3. Views: `estoque/views.py`
4. Teste: `python manage.py test`

### 📊 **Gestor de Projeto**
1. README: [README_NOVO.md](README_NOVO.md)
2. Checklist: [CHECKLIST.md](docs/CHECKLIST.md)
3. Status: Verifique commits no Git

### 🆕 **Novo no Projeto**
1. **PASSO 1:** Leia [LEIA-ME-PRIMEIRO.txt](docs/LEIA-ME-PRIMEIRO.txt)
2. **PASSO 2:** Execute `scripts\iniciar.bat`
3. **PASSO 3:** Explore [ORGANIZACAO.md](ORGANIZACAO.md)
4. **PASSO 4:** Teste o sistema localmente

---

## 🔍 BUSCAR ALGO?

### Por Tipo de Arquivo:
- **📄 HTML:** `templates/`
- **🎨 CSS:** `static/css/` ou `static/scss/`
- **⚡ JavaScript:** `static/js/`
- **🐍 Python:** `estoque/`, `core/`, `gestaoestoque/`
- **📚 Docs:** `docs/`
- **🔧 Scripts:** `scripts/`
- **⚙️ Config:** `config/`, `.env`, `.gitignore`

### Por Funcionalidade:
- **Dashboard:** `templates/dashboard.html` + `estoque/views.py`
- **Produtos:** `estoque/models.py` (class Produto)
- **Movimentações:** `estoque/models.py` (class Movimentacao)
- **Alertas:** `estoque/models.py` (class Alerta)
- **Admin:** `estoque/admin.py`
- **Rotas:** `estoque/urls.py` + `gestaoestoque/urls.py`

---

## 💡 DICAS RÁPIDAS

1. ⭐ **Sempre comece por:** `docs/LEIA-ME-PRIMEIRO.txt`
2. 🔍 **Perdido?** Consulte `ORGANIZACAO.md`
3. 🚀 **Iniciar rápido:** `scripts\iniciar.bat`
4. 🎨 **CSS pronto:** `static/css/style.css` (já compilado!)
5. 🎲 **Dados teste:** `python manage.py criar_dados_exemplo`
6. 📖 **Dúvidas:** Veja documentação em `docs/`

---

## ❓ FAQ - Onde Está...?

| Pergunta | Resposta |
|----------|----------|
| Onde estão os templates? | `templates/` |
| Onde edito o CSS? | `static/css/style.css` ou `static/scss/style.scss` |
| Onde ficam as imagens? | `static/images/` |
| Onde estão os models? | `estoque/models.py` |
| Onde configurar o Django? | `gestaoestoque/settings.py` |
| Onde está a documentação? | `docs/` |
| Como iniciar o servidor? | `python manage.py runserver` |
| Como criar admin? | `python manage.py createsuperuser` |

---

## 🎯 OBJETIVOS DO PROJETO

- ✅ Sistema de gestão de estoque
- ✅ Dashboard interativo
- ✅ Controle de movimentações
- ✅ Alertas de estoque
- ✅ Interface moderna e responsiva
- ✅ Admin completo
- ✅ Documentação organizada

---

## 📞 SUPORTE

- **Documentação:** `docs/`
- **Issues:** GitHub Issues
- **README:** `README_NOVO.md`
- **Organização:** `ORGANIZACAO.md`

---

**✨ Use este índice como ponto de partida para navegar no projeto!**

_Última atualização: 08/11/2025_
