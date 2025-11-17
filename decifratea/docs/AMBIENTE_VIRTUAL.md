# 🐍 Gerenciamento de Ambiente Virtual

## Por que .venv311?

O projeto está configurado para usar `.venv311` como nome do ambiente virtual por padrão, seguindo a convenção do projeto profissional `site-padrao`. Isso oferece várias vantagens:

### ✅ Vantagens

1. **Versão específica**: Nome indica claramente que usa Python 3.11
2. **Múltiplos ambientes**: Permite ter `.venv310`, `.venv311`, `.venv312` lado a lado
3. **Consistência**: Mesma estrutura do projeto profissional
4. **Fácil identificação**: Qualquer um sabe qual versão está sendo usada

## 🚀 Como Criar o Ambiente Virtual

### Método 1: Script Automático (Recomendado)

#### Windows (PowerShell)
```powershell
.\criar_venv.ps1
```

#### Linux/Mac
```bash
chmod +x criar_venv.sh
./criar_venv.sh
```

### Método 2: Manual

#### Windows
```powershell
python -m venv .venv311
```

#### Linux/Mac
```bash
python3.11 -m venv .venv311
```

## 🔌 Como Ativar o Ambiente Virtual

### Windows

#### PowerShell
```powershell
.\.venv311\Scripts\Activate.ps1
```

#### CMD
```cmd
.venv311\Scripts\activate.bat
```

### Linux/Mac
```bash
source .venv311/bin/activate
```

## 📦 Instalando Dependências

Após ativar o ambiente virtual:

```bash
# Atualizar pip primeiro
pip install --upgrade pip

# Instalar dependências de desenvolvimento
pip install -r requirements/dev.txt

# Ou para produção
pip install -r requirements/production.txt
```

## 🔄 Alternativas de Nome

Se preferir usar outro nome, você pode:

### Usar .venv (padrão Python)
```bash
python -m venv .venv
```

### Usar venv
```bash
python -m venv venv
```

### Usar nome customizado
```bash
python -m venv meu_ambiente
```

**Nota**: O `.gitignore` já está configurado para ignorar `.venv`, `.venv311`, `venv/` e `env/`.

## 🛠️ Comandos Úteis

### Verificar qual ambiente está ativo
```bash
# Windows
where python

# Linux/Mac
which python
```

### Desativar ambiente virtual
```bash
deactivate
```

### Remover ambiente virtual
```bash
# Windows
Remove-Item -Recurse -Force .venv311

# Linux/Mac
rm -rf .venv311
```

### Recriar do zero
```bash
# Remover
rm -rf .venv311

# Criar novamente
python -m venv .venv311

# Ativar
source .venv311/bin/activate  # ou .\.venv311\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements/dev.txt
```

## 🎯 Melhores Práticas

1. **Sempre ative o ambiente antes de trabalhar**
   ```bash
   source .venv311/bin/activate
   ```

2. **Mantenha requirements atualizado**
   ```bash
   pip freeze > requirements/dev.txt
   ```

3. **Use o ambiente correto no VSCode**
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Escolha `.venv311/Scripts/python.exe` (Windows)
   - Ou `.venv311/bin/python` (Linux/Mac)

4. **Verifique se está ativo antes de instalar pacotes**
   ```bash
   # Deve mostrar o caminho do .venv311
   which python  # Linux/Mac
   where python  # Windows
   ```

## 🐛 Troubleshooting

### Erro: "Execution of scripts is disabled on this system"

**Windows PowerShell**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "python: command not found"

Instale Python 3.11+ ou adicione ao PATH.

### Erro: "No module named 'venv'"

```bash
# Ubuntu/Debian
sudo apt-get install python3.11-venv

# Fedora
sudo dnf install python3-venv
```

### VSCode não reconhece o ambiente

1. Recarregue a janela: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Selecione o interpretador: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Escolha `.venv311/Scripts/python.exe`

## 📋 Checklist de Configuração

- [ ] Python 3.11+ instalado
- [ ] Ambiente virtual criado (`.venv311`)
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements/dev.txt`)
- [ ] VSCode configurado para usar `.venv311`
- [ ] Terminal mostra `(.venv311)` no prompt

## 🎓 Dicas Avançadas

### Criar requirements separado para seu ambiente
```bash
pip freeze > requirements-local.txt
```

### Comparar pacotes instalados
```bash
pip list --outdated
```

### Limpar cache do pip
```bash
pip cache purge
```

### Verificar pacotes com vulnerabilidades
```bash
pip install safety
safety check
```

## 📞 Ajuda

Se tiver problemas:

1. Veja o `CHECKLIST.md`
2. Consulte o `README.md`
3. Revise o `INICIO_RAPIDO.md`

---

**Última atualização**: Novembro 2025
