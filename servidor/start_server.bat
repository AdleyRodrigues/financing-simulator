@echo off
REM Script para iniciar o JSON Server no Windows

echo =========================================
echo  Controle de Divida - JSON Server
echo =========================================
echo.

REM Ir para o diretorio do servidor
cd /d "%~dp0"

REM Verificar se db.json existe
if not exist "db.json" (
    echo [ERRO] Arquivo db.json nao encontrado!
    echo.
    echo Este script deve estar na pasta 'servidor'
    echo.
    pause
    exit /b 1
)

REM Verificar se o Node.js esta instalado
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Node.js nao encontrado!
    echo.
    echo Por favor, instale o Node.js em: https://nodejs.org
    echo.
    pause
    exit /b 1
)

REM Detectar gerenciador de pacotes disponivel
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

echo [INFO] Usando gerenciador: %PKG_MANAGER%
echo.

REM Verificar se node_modules existe
if not exist "node_modules" (
    echo [INFO] Instalando dependencias...
    %INSTALL_CMD%
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao instalar dependencias
        pause
        exit /b 1
    )
    echo.
)

echo [OK] Iniciando JSON Server na porta 3000...
echo.
echo Endpoints disponiveis:
echo   - http://localhost:3000/registros
echo   - http://localhost:3000/config
echo.
echo Interface web: http://localhost:3000
echo.
echo Pressione Ctrl+C para parar o servidor
echo =========================================
echo.

%RUN_CMD%
