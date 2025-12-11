@echo off
REM Script para iniciar o Controle de Dívida completo
REM Inicia o servidor Node.js e a aplicação Python automaticamente

chcp 65001 >nul
setlocal enabledelayedexpansion

echo =========================================
echo   Controle de Dívida - Iniciando...
echo =========================================
echo.

REM Verificar se Python está instalado
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado!
    echo.
    echo Por favor, instale o Python em: https://www.python.org
    echo.
    pause
    exit /b 1
)

REM Verificar se Node.js está instalado
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Node.js não encontrado!
    echo.
    echo O servidor não será iniciado. A aplicação rodará em modo offline.
    echo.
    set SERVIDOR_DISPONIVEL=0
    goto :INICIAR_APP
)

set SERVIDOR_DISPONIVEL=1

REM Ir para o diretório do servidor
cd /d "%~dp0servidor"

REM Verificar se db.json existe
if not exist "db.json" (
    echo [INFO] Criando arquivo db.json...
    echo { > db.json
    echo   "registros": [], >> db.json
    echo   "config": [] >> db.json
    echo } >> db.json
)

REM Detectar gerenciador de pacotes disponível
set PKG_MANAGER=npm
set INSTALL_CMD=npm install
set RUN_CMD=npm start

where pnpm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PKG_MANAGER=pnpm
    set INSTALL_CMD=pnpm install
    set RUN_CMD=pnpm start
) else (
    where yarn >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PKG_MANAGER=yarn
        set INSTALL_CMD=yarn install
        set RUN_CMD=yarn start
    )
)

REM Verificar se node_modules existe
if not exist "node_modules" (
    echo [INFO] Instalando dependências do servidor...
    echo.
    %INSTALL_CMD%
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao instalar dependências
        echo A aplicação rodará em modo offline.
        echo.
        set SERVIDOR_DISPONIVEL=0
        goto :INICIAR_APP
    )
    echo.
)

REM Voltar para a raiz
cd /d "%~dp0"

REM Iniciar servidor em background
if %SERVIDOR_DISPONIVEL% EQU 1 (
    echo [INFO] Iniciando servidor JSON Server...
    
    REM Iniciar servidor em janela minimizada
    start "JSON Server - Controle de Dívida" /min cmd /c "cd /d %~dp0servidor && %RUN_CMD%"
    
    REM Aguardar servidor iniciar (3 segundos)
    echo [INFO] Aguardando servidor iniciar...
    timeout /t 3 /nobreak >nul
    
    REM Verificar se servidor está rodando na porta 3000
    netstat -an | findstr ":3000" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Servidor iniciado na porta 3000
    ) else (
        echo [AVISO] Servidor pode não ter iniciado corretamente
    )
    echo.
)

:INICIAR_APP
REM Verificar se tkcalendar está instalado
python -c "import tkcalendar" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Instalando dependência tkcalendar...
    python -m pip install tkcalendar --quiet
    echo.
)

REM Iniciar aplicação Python
echo [INFO] Iniciando aplicação...
echo.
echo =========================================
echo   Aplicação iniciada!
echo =========================================
echo.

cd /d "%~dp0"
python controle_divida.py

REM Quando a aplicação fechar, encerrar o servidor
if %SERVIDOR_DISPONIVEL% EQU 1 (
    echo.
    echo [INFO] Encerrando servidor...
    
    REM Tentar encontrar e matar processos Node.js que estão usando a porta 3000
    REM Usar netstat para encontrar PID usando a porta 3000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        set SERVER_PID=%%a
        if defined SERVER_PID (
            taskkill /F /PID !SERVER_PID! >nul 2>&1
            if !ERRORLEVEL! EQU 0 (
                echo [OK] Servidor encerrado (PID: !SERVER_PID!)
            )
        )
    )
)

echo.
echo =========================================
echo   Aplicação encerrada.
echo =========================================
echo.
pause

