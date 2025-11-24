@echo off
REM Script rápido de inicialização - Windows Batch
REM Execute este arquivo clicando duas vezes nele

echo ========================================
echo   Sistema de Gestao de Estoque
echo   Inicializacao Rapida
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Instalando Django...
pip install django pillow python-dateutil

echo.
echo [2/6] Criando migracoes...
python manage.py makemigrations

echo.
echo [3/6] Aplicando migracoes...
python manage.py migrate

echo.
echo [4/6] Deseja criar dados de exemplo? (S/N)
set /p resposta="Digite S para sim ou N para nao: "
if /i "%resposta%"=="S" (
    echo Criando dados de exemplo...
    python manage.py criar_dados_exemplo
    echo.
    echo CREDENCIAIS CRIADAS:
    echo Username: admin
    echo Password: admin123
) else (
    echo.
    echo [4/6] Criando superusuario...
    python manage.py createsuperuser
)

echo.
echo ========================================
echo   Configuracao Concluida!
echo ========================================
echo.
echo Para iniciar o servidor, execute:
echo   python manage.py runserver
echo.
echo Ou simplesmente pressione ENTER agora...
pause

cls
echo Iniciando servidor...
echo.
echo Dashboard: http://127.0.0.1:8000/
echo Admin:     http://127.0.0.1:8000/admin/
echo.
echo Pressione CTRL+C para parar o servidor
echo.
python manage.py runserver
