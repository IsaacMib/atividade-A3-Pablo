# 📋 ORDEM DE EXECUÇÃO - SETUP COMPLETO

Execute estes comandos **NESTA ORDEM** para configurar o projeto completamente.

## ✅ Passo 1: Criar Ambiente Virtual

```powershell
# Criar .venv311 automaticamente
.\criar_venv.ps1
```

**Resultado esperado**: ✓ Ambiente virtual .venv311 criado

---

## ✅ Passo 2: Ativar Ambiente Virtual

```powershell
# PowerShell
.\.venv311\Scripts\Activate.ps1

# Ou CMD
.venv311\Scripts\activate.bat
```

**Resultado esperado**: `(.venv311)` aparece no prompt

---

## ✅ Passo 3: Instalar Dependências Python

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements/dev.txt
```

**Resultado esperado**: Todas as dependências instaladas sem erros

---

## ✅ Passo 4: Instalar Dependências Node

```bash
npm install
```

**Resultado esperado**: node_modules/ criado com sucesso

---

## ✅ Passo 5: Criar Arquivo .env

```powershell
# Se não existe ainda
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

**Resultado esperado**: Arquivo .env criado

---

## ✅ Passo 6: Criar Migrações do Core

```bash
python manage.py makemigrations core
```

**Resultado esperado**: 
```
Migrations for 'core':
  core\migrations\0001_initial.py
    - Create model ConfiguracaoSistema
    - Create model Log
```

---

## ✅ Passo 7: Aplicar Migrações

```bash
python manage.py migrate
```

**Resultado esperado**: 
```
Running migrations:
  Applying core.0001_initial... OK
  (outras migrações...)
```

---

## ✅ Passo 8: Setup Inicial

```bash
python manage.py setup_inicial
```

**Resultado esperado**:
```
✓ Configuração do sistema criada
✅ Setup inicial concluído com sucesso!
```

---

## ✅ Passo 9: Criar Superusuário

```bash
python manage.py createsuperuser
```

**Preencha**:
- Username: admin (ou seu preferido)
- Email: seu@email.com
- Password: (senha segura)

**Resultado esperado**: `Superuser created successfully.`

---

## ✅ Passo 10: Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

**Resultado esperado**: Arquivos copiados para staticfiles/

---

## ✅ Passo 11: Compilar Frontend

```bash
# Em um novo terminal (mantendo o outro ativo)
npm run dev
```

**Resultado esperado**: Vite rodando e compilando assets

---

## ✅ Passo 12: Iniciar Servidor

```bash
# No terminal principal
python manage.py runserver
```

**Resultado esperado**:
```
Starting development server at http://127.0.0.1:8000/
```

---

## ✅ Passo 13: Verificar Admin

1. Acesse: http://localhost:8000/admin/
2. Faça login com o superusuário criado
3. Verifique se aparece:
   - Core → Configuração do Sistema
   - Core → Logs

---

## ✅ Passo 14: Configurar Sistema

No admin, vá em **Core → Configuração do Sistema** e preencha:
- Nome do Sistema
- Email de Contato
- Logo (opcional)
- Cores (opcional)

**Clique em Salvar**

---

## ✅ Passo 15: Verificar Info do Sistema

```bash
python manage.py info_sistema
```

**Resultado esperado**: Exibe informações completas do sistema

---

## 🎉 PRONTO!

Se todos os passos foram executados com sucesso, seu projeto está:

✅ Ambiente virtual configurado (.venv311)
✅ Dependências instaladas
✅ Banco de dados migrado
✅ Core app funcionando
✅ Admin configurado
✅ Frontend compilando
✅ Servidor rodando

---

## 🧪 TESTE OPCIONAL: Executar Testes

```bash
# Testar core
pytest core/

# Ou todos os testes
pytest
```

---

## 📝 COMANDOS ÚTEIS DO DIA A DIA

```bash
# Informações do sistema
python manage.py info_sistema

# Limpar logs antigos
python manage.py limpar_logs --dias 30

# Ver comandos disponíveis
make help

# Formatar código
make format

# Verificar qualidade
make lint
```

---

## 🆘 PROBLEMAS?

### Erro: "No module named 'django'"
**Solução**: Ative o ambiente virtual
```powershell
.\.venv311\Scripts\Activate.ps1
```

### Erro: "No migrations to apply"
**Solução**: Crie as migrações primeiro
```bash
python manage.py makemigrations core
python manage.py migrate
```

### Erro: "port is already in use"
**Solução**: Use outra porta
```bash
python manage.py runserver 8001
```

### Frontend não carrega
**Solução**: Compile novamente
```bash
npm run build
```

---

## 📚 DOCUMENTAÇÃO

- **LEIA_ISSO_PRIMEIRO.txt** - Visão geral
- **CORE_E_VENV.txt** - Detalhes core e .venv311
- **CORE_APP.md** - Doc completa do core
- **AMBIENTE_VIRTUAL.md** - Guia do .venv311
- **README.md** - Doc completa
- **CHECKLIST.md** - Verificação completa

---

**Execute nesta ordem e terá um projeto 100% funcional!** 🚀
