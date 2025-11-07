#!/bin/bash
# Script para iniciar o JSON Server no Linux/Mac/Git Bash

echo "========================================="
echo "  Controle de Dívida - JSON Server"
echo "========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "db.json" ]; then
    echo "[ERRO] Arquivo db.json não encontrado!"
    echo ""
    echo "Este script deve ser executado de dentro da pasta 'servidor':"
    echo "  cd servidor"
    echo "  ./start_server.sh"
    echo ""
    exit 1
fi

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "[ERRO] Node.js não encontrado!"
    echo ""
    echo "Por favor, instale o Node.js em: https://nodejs.org"
    echo ""
    exit 1
fi

# Verificar se pnpm está instalado (preferencial)
if command -v pnpm &> /dev/null; then
    PKG_MANAGER="pnpm"
    INSTALL_CMD="pnpm install"
    RUN_CMD="pnpm start"
elif command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
    INSTALL_CMD="yarn install"
    RUN_CMD="yarn start"
else
    PKG_MANAGER="npm"
    INSTALL_CMD="npm install"
    RUN_CMD="npm start"
fi

echo "[INFO] Usando gerenciador: $PKG_MANAGER"
echo ""

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "[INFO] Instalando dependências..."
    $INSTALL_CMD
    
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao instalar dependências"
        exit 1
    fi
    echo ""
fi

echo "[OK] Iniciando JSON Server na porta 3000..."
echo ""
echo "Endpoints disponíveis:"
echo "  - http://localhost:3000/registros"
echo "  - http://localhost:3000/config"
echo ""
echo "Interface web: http://localhost:3000"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "========================================="
echo ""

$RUN_CMD
