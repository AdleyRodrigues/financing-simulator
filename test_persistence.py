#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para a camada de persistência.
Testa as operações CRUD com o JSON Server.
"""

import persistence
from datetime import datetime

def teste_conexao():
    """Testa a conexão com o servidor."""
    print("🔍 Testando conexão com JSON Server...")
    
    if persistence.verificar_conexao():
        print("✅ Conexão estabelecida com sucesso!")
        return True
    else:
        print("❌ Não foi possível conectar ao JSON Server")
        print("   Certifique-se de que está rodando: json-server --watch db.json --port 3000")
        return False

def teste_config():
    """Testa leitura da configuração."""
    print("\n🔍 Testando leitura de configuração...")
    
    try:
        config = persistence.read_config()
        print(f"✅ Configuração lida: {config}")
        print(f"   - Dívida inicial: R$ {config['divida_inicial']:,.2f}")
        print(f"   - Taxa de juros: {config['taxa']*100}%")
    except Exception as e:
        print(f"❌ Erro ao ler configuração: {e}")

def teste_crud():
    """Testa operações CRUD de registros."""
    print("\n🔍 Testando operações CRUD...")
    
    # 1. Listar registros existentes
    print("\n1️⃣ Listando registros...")
    try:
        registros = persistence.read_all_registros()
        print(f"✅ Encontrados {len(registros)} registros")
        for reg in registros:
            data_pagamento = reg.get("data_pagamento") or reg.get("data", "-")
            data_referencia = reg.get("data_referencia") or reg.get("data", "-")
            print(
                f"   - Mês {reg['mes']}: pago em {data_pagamento}, "
                f"ref. {data_referencia} - R$ {reg['valor']:.2f} ({reg['status']})"
            )
    except Exception as e:
        print(f"❌ Erro ao listar: {e}")
        return
    
    # 2. Criar novo registro de teste
    print("\n2️⃣ Criando novo registro de teste...")
    novo_registro = {
        "mes": len(registros) + 1,
        "data": datetime.now().strftime("%d/%m/%Y"),
        "data_pagamento": datetime.now().strftime("%d/%m/%Y"),
        "data_referencia": datetime.now().strftime("%d/%m/%Y"),
        "valor": 1000.00,
        "juros": 500.00,
        "amort": 500.00,
        "saldo": 49000.00,
        "status": "Pago",
        "tipo": "pagamento",
        "createdAt": datetime.now().isoformat() + "Z"
    }
    
    try:
        resultado = persistence.create_registro(novo_registro)
        registro_id = resultado['id']
        print(f"✅ Registro criado com ID: {registro_id}")
    except Exception as e:
        print(f"❌ Erro ao criar: {e}")
        return
    
    # 3. Atualizar status do registro
    print("\n3️⃣ Atualizando status para 'Pendente'...")
    try:
        resultado = persistence.update_registro(registro_id, {"status": "Pendente"})
        print(f"✅ Status atualizado: {resultado['status']}")
    except Exception as e:
        print(f"❌ Erro ao atualizar: {e}")
    
    # 4. Deletar o registro de teste
    print("\n4️⃣ Deletando registro de teste...")
    try:
        persistence.delete_registro(registro_id)
        print(f"✅ Registro {registro_id} deletado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao deletar: {e}")
    
    # 5. Verificar que foi deletado
    print("\n5️⃣ Verificando que foi deletado...")
    try:
        registros_final = persistence.read_all_registros()
        print(f"✅ Registros restantes: {len(registros_final)}")
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("  TESTE DA CAMADA DE PERSISTÊNCIA")
    print("=" * 60)
    
    # Verificar se persistência está ativada
    if not persistence.PERSISTENCIA_ATIVA:
        print("\n⚠️  AVISO: Persistência está DESATIVADA no módulo")
        print("   Configure PERSISTENCIA_ATIVA = True em persistence.py")
        return
    
    # Teste 1: Conexão
    if not teste_conexao():
        return
    
    # Teste 2: Configuração
    teste_config()
    
    # Teste 3: CRUD
    teste_crud()
    
    print("\n" + "=" * 60)
    print("✅ Todos os testes concluídos!")
    print("=" * 60)

if __name__ == "__main__":
    main()
