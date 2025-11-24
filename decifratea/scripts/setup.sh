#!/bin/bash
# Script de setup para desenvolvimento - Linux/Mac

set -e

echo "🚀 Iniciando setup do projeto Gestão de Estoque..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica Python
echo "📦 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11+"
    exit 1
fi
echo -e "${GREEN}✓ Python encontrado${NC}"

# Verifica Node.js
echo "📦 Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale Node.js 18+"
    exit 1
fi
echo -e "${GREEN}✓ Node.js encontrado${NC}"

# Cria ambiente virtual
echo "🐍 Criando ambiente virtual..."
python3 -m venv .venv
echo -e "${GREEN}✓ Ambiente virtual criado${NC}"

# Ativa ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source .venv/bin/activate

# Atualiza pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instala dependências Python
echo "📚 Instalando dependências Python..."
pip install -r requirements/dev.txt
echo -e "${GREEN}✓ Dependências Python instaladas${NC}"

# Instala dependências Node
echo "📚 Instalando dependências Node.js..."
npm install
echo -e "${GREEN}✓ Dependências Node.js instaladas${NC}"

# Cria arquivo .env
if [ ! -f .env ]; then
    echo "⚙️  Criando arquivo .env..."
    cp .env.example .env
    echo -e "${GREEN}✓ Arquivo .env criado${NC}"
    echo -e "${YELLOW}⚠️  Não esqueça de configurar suas variáveis em .env${NC}"
else
    echo -e "${YELLOW}⚠️  Arquivo .env já existe${NC}"
fi

# Cria diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs staticfiles media

# Configura pre-commit hooks
echo "🎣 Configurando pre-commit hooks..."
pre-commit install
echo -e "${GREEN}✓ Pre-commit hooks configurados${NC}"

# Executa migrações
echo "🗄️  Executando migrações..."
python manage.py migrate
echo -e "${GREEN}✓ Migrações aplicadas${NC}"

# Coleta arquivos estáticos
echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Arquivos estáticos coletados${NC}"

echo ""
echo -e "${GREEN}✅ Setup concluído com sucesso!${NC}"
echo ""
echo "📝 Próximos passos:"
echo "1. Ative o ambiente virtual: source .venv/bin/activate"
echo "2. Crie um superusuário: python manage.py createsuperuser"
echo "3. Execute o servidor: make run"
echo "4. Acesse: http://localhost:8000"
echo ""
echo "🎉 Bom desenvolvimento!"
