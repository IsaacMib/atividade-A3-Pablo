# Script de inicialização do projeto
# Execute este script para configurar o projeto pela primeira vez

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Sistema de Gestão de Estoque" -ForegroundColor Cyan
Write-Host "  Inicializando projeto..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o Django está instalado
Write-Host "1. Verificando Django..." -ForegroundColor Yellow
try {
    python -c "import django; print(f'Django {django.get_version()} instalado')"
} catch {
    Write-Host "Django não encontrado. Instalando..." -ForegroundColor Red
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "2. Criando migrações..." -ForegroundColor Yellow
python manage.py makemigrations

Write-Host ""
Write-Host "3. Aplicando migrações..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "4. Criando superusuário..." -ForegroundColor Yellow
Write-Host "   (Você precisará definir username e senha)" -ForegroundColor Gray
python manage.py createsuperuser

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Configuração concluída!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar o servidor, execute:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Yellow
Write-Host ""
