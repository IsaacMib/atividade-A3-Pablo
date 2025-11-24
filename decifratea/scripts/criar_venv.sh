#!/bin/bash
# Script para criar e configurar ambiente virtual com Python 3.11
# Uso: ./criar_venv.sh

echo "🐍 Criando ambiente virtual com Python 3.11..."

# Verifica se Python 3.11 está disponível
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    # Verifica versão
    version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$version" == "3.11" ]; then
        PYTHON_CMD="python3"
    else
        echo "❌ Python 3.11 não encontrado. Versão atual: $version"
        echo "Por favor, instale Python 3.11+"
        exit 1
    fi
else
    echo "❌ Python não encontrado"
    exit 1
fi

echo "✓ Usando: $PYTHON_CMD ($($PYTHON_CMD --version))"

# Cria ambiente virtual com nome .venv311
if [ -d ".venv311" ]; then
    echo "⚠️  Diretório .venv311 já existe"
    read -p "Deseja recriar? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf .venv311
    else
        echo "Operação cancelada"
        exit 0
    fi
fi

$PYTHON_CMD -m venv .venv311

echo "✓ Ambiente virtual .venv311 criado com sucesso!"
echo ""
echo "📝 Para ativar o ambiente virtual:"
echo "   source .venv311/bin/activate    # Linux/Mac"
echo "   .venv311\\Scripts\\activate      # Windows"
echo ""
echo "Depois de ativar, instale as dependências:"
echo "   pip install -r requirements/dev.txt"
