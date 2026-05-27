@echo off
REM Script para iniciar o Controle de Divida
REM Arquitetura 100%% Python + SQLite — Node.js nao e mais necessario

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo.
echo =========================================
echo   Controle de Divida
echo =========================================
echo.

REM Mudar para o diretorio do script
cd /d "%~dp0"

REM Verificar se Python esta instalado
where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale em: https://www.python.org
    echo Certifique-se de adicionar Python ao PATH.
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python encontrado!
echo.

REM Verificar sintaxe do arquivo Python antes de abrir
echo [INFO] Verificando integridade do codigo...
python -m py_compile controle_divida.py >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Erro no arquivo controle_divida.py!
    echo Execute manualmente para ver o erro: python controle_divida.py
    echo.
    pause
    exit /b 1
)
echo [OK] Codigo verificado!
echo.

REM Iniciar aplicacao em modo silencioso (sem console)
echo [INFO] Iniciando aplicacao...
start "Controle de Divida" pythonw controle_divida.py

REM Aguardar 1 segundo e fechar o terminal automaticamente
timeout /t 1 /nobreak >nul
exit
