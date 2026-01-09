@echo off
REM Script para iniciar o Controle de Divida completo
REM Inicia o servidor Node.js e a aplicacao Python automaticamente

REM Garantir que o terminal nao feche imediatamente em caso de erro
setlocal enabledelayedexpansion

REM Forcar exibicao de mensagens
echo.
echo =========================================
echo   INICIANDO SCRIPT...
echo =========================================
echo.

REM Mudar para o diretorio do script PRIMEIRO
echo [DEBUG] Tentando acessar diretorio: %~dp0
cd /d "%~dp0"
if errorlevel 1 (
    echo.
    echo [ERRO CRITICO] Nao foi possivel acessar o diretorio do script!
    echo Caminho tentado: %~dp0
    echo.
    echo Pressione qualquer tecla para sair...
    pause
    exit /b 1
)
echo [DEBUG] Diretorio alterado com sucesso
echo.

REM Tentar configurar encoding
chcp 65001 >nul 2>&1

echo =========================================
echo   Controle de Divida - Iniciando...
echo =========================================
echo.
echo Diretorio atual: %CD%
echo.

REM Verificar se Python esta instalado
echo [INFO] Verificando Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale o Python em: https://www.python.org
    echo Certifique-se de adicionar Python ao PATH durante a instalacao.
    echo.
    echo Pressione qualquer tecla para sair...
    pause
    exit /b 1
)

REM Testar se Python funciona
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python encontrado mas nao esta funcionando corretamente!
    echo.
    echo Pressione qualquer tecla para sair...
    pause
    exit /b 1
)

python --version
echo [OK] Python encontrado!
echo.

REM Verificar se Node.js esta instalado
echo [INFO] Verificando Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Node.js nao encontrado!
    echo.
    echo O servidor nao sera iniciado. A aplicacao rodara em modo offline.
    echo.
    set SERVIDOR_DISPONIVEL=0
    goto :INICIAR_APP
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Node.js encontrado mas nao esta funcionando corretamente!
    echo A aplicacao rodara em modo offline.
    echo.
    set SERVIDOR_DISPONIVEL=0
    goto :INICIAR_APP
)

node --version
echo [OK] Node.js encontrado!
echo.

set SERVIDOR_DISPONIVEL=1

REM Ir para o diretorio do servidor
cd /d "%~dp0servidor"

REM Verificar se db.json existe
if not exist "db.json" (
    echo [INFO] Criando arquivo db.json...
    echo { > db.json
    echo   "registros": [], >> db.json
    echo   "config": [] >> db.json
    echo } >> db.json
)

REM Detectar gerenciador de pacotes disponivel
set PKG_MANAGER=npm
set INSTALL_CMD=npm install
set RUN_CMD=npm start

where pnpm >nul 2>&1
if not errorlevel 1 (
    set PKG_MANAGER=pnpm
    set INSTALL_CMD=pnpm install
    set RUN_CMD=pnpm start
) else (
    where yarn >nul 2>&1
    if not errorlevel 1 (
        set PKG_MANAGER=yarn
        set INSTALL_CMD=yarn install
        set RUN_CMD=yarn start
    )
)

REM Verificar se node_modules existe
if not exist "node_modules" (
    echo [INFO] Instalando dependencias do servidor...
    echo.
    call %INSTALL_CMD%
    
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias
        echo A aplicacao rodara em modo offline.
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
    start "JSON Server" /min cmd /c "cd /d %~dp0servidor && %RUN_CMD%"
    
    REM Aguardar servidor iniciar (3 segundos)
    echo [INFO] Aguardando servidor iniciar...
    timeout /t 3 /nobreak >nul
    
    REM Verificar se servidor esta rodando na porta 3000
    netstat -an | findstr ":3000" >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] Servidor pode nao ter iniciado corretamente
    ) else (
        echo [OK] Servidor iniciado na porta 3000
    )
    echo.
)

:INICIAR_APP
REM Voltar para o diretorio raiz
cd /d "%~dp0"

REM Verificar se o arquivo Python existe
if not exist "controle_divida.py" (
    echo [ERRO] Arquivo controle_divida.py nao encontrado!
    echo.
    echo O arquivo deve estar no diretorio: %CD%
    echo.
    echo Pressione qualquer tecla para sair...
    pause
    exit /b 1
)

REM Verificar se tkcalendar esta instalado
echo [INFO] Verificando dependencias Python...
python -c "import tkcalendar" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencia tkcalendar...
    python -m pip install tkcalendar --quiet
    if errorlevel 1 (
        echo [AVISO] Falha ao instalar tkcalendar. Continuando mesmo assim...
    ) else (
        echo [OK] tkcalendar instalado com sucesso!
    )
    echo.
)

REM Verificar sintaxe do arquivo Python
echo [INFO] Verificando sintaxe do arquivo Python...
python -m py_compile controle_divida.py >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Erro de sintaxe no arquivo controle_divida.py!
    echo.
    echo Executando verificacao detalhada...
    python -m py_compile controle_divida.py
    echo.
    echo Pressione qualquer tecla para sair...
    pause
    exit /b 1
)
echo [OK] Sintaxe do arquivo Python esta correta!
echo.

REM Iniciar aplicacao Python
echo [INFO] Iniciando aplicacao Python...
echo.
echo =========================================
echo   Aplicacao iniciada!
echo =========================================
echo.

REM Executar Python e capturar erros
echo Executando: python -u controle_divida.py
echo.
REM Usar -u para modo unbuffered (saida imediata)
python -u controle_divida.py
set PYTHON_EXIT_CODE=%ERRORLEVEL%

if %PYTHON_EXIT_CODE% NEQ 0 (
    echo.
    echo =========================================
    echo   [ERRO] Aplicacao nao iniciou corretamente!
    echo =========================================
    echo.
    echo Codigo de erro: %PYTHON_EXIT_CODE%
    echo.
    echo Possiveis causas:
    echo - Erro de sintaxe no arquivo controle_divida.py
    echo - Dependencias Python nao instaladas
    echo - Problema com o ambiente Python
    echo.
    echo Tente executar manualmente:
    echo   python controle_divida.py
    echo.
    echo Para ver erros detalhados, execute:
    echo   python -u controle_divida.py
    echo.
)

REM Quando a aplicacao fechar, encerrar o servidor
if %SERVIDOR_DISPONIVEL% EQU 1 (
    echo.
    echo [INFO] Encerrando servidor...
    
    REM Tentar encontrar e matar processos Node.js que estao usando a porta 3000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        set SERVER_PID=%%a
        if defined SERVER_PID (
            taskkill /F /PID !SERVER_PID! >nul 2>&1
            if not errorlevel 1 (
                echo [OK] Servidor encerrado (PID: !SERVER_PID!)
            )
        )
    )
)

echo.
echo =========================================
echo   Aplicacao encerrada.
echo =========================================
echo.
echo Pressione qualquer tecla para fechar...
pause
