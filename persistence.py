#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camada de persistência para comunicação com JSON Server.
Usa apenas bibliotecas padrão do Python (urllib).
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Any

# Configuração
BASE_URL = "http://localhost:3000"
TIMEOUT = 3  # segundos
PERSISTENCIA_ATIVA = True


class PersistenceError(Exception):
    """Erro genérico de persistência."""
    pass


def _fazer_requisicao(
    url: str,
    metodo: str = "GET",
    dados: Optional[Dict[str, Any]] = None,
    timeout: int = TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Faz uma requisição HTTP ao JSON Server.
    
    Args:
        url: URL completa do endpoint
        metodo: GET, POST, PATCH, DELETE, etc.
        dados: Dicionário a ser enviado como JSON (para POST/PATCH)
        timeout: Timeout da requisição em segundos
    
    Returns:
        Dicionário com a resposta JSON ou None
    
    Raises:
        PersistenceError: Se houver erro de rede ou HTTP
    """
    if not PERSISTENCIA_ATIVA:
        raise PersistenceError("Persistência desativada")
    
    # LOG: Requisição iniciada
    print(f"[PERSISTENCE] {metodo} {url}")
    if dados:
        print(f"[PERSISTENCE] Dados: {json.dumps(dados, indent=2)}")
    
    try:
        headers = {"Content-Type": "application/json"}
        
        if dados is not None:
            data_bytes = json.dumps(dados).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=metodo)
        else:
            req = urllib.request.Request(url, headers=headers, method=metodo)
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            print(f"[PERSISTENCE] Status: {response.status}")
            
            if response.status == 204:  # No Content (DELETE bem-sucedido)
                print(f"[PERSISTENCE] ✅ {metodo} bem-sucedido (No Content)")
                return None
            
            body = response.read().decode('utf-8')
            if not body:
                print(f"[PERSISTENCE] ⚠️  Resposta vazia")
                return None
            
            resultado = json.loads(body)
            print(f"[PERSISTENCE] ✅ Resposta recebida")
            return resultado
    
    except urllib.error.HTTPError as e:
        print(f"[PERSISTENCE] ❌ Erro HTTP {e.code}: {e.reason}")
        raise PersistenceError(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"[PERSISTENCE] ❌ Erro de conexão: {e.reason}")
        raise PersistenceError(f"Erro de conexão: {e.reason}")
    except json.JSONDecodeError as e:
        print(f"[PERSISTENCE] ❌ Erro ao decodificar JSON: {e}")
        raise PersistenceError(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"[PERSISTENCE] ❌ Erro inesperado: {e}")
        raise PersistenceError(f"Erro inesperado: {e}")


def read_all_registros() -> List[Dict[str, Any]]:
    """
    Busca todos os registros do servidor.
    
    Returns:
        Lista de dicionários com os registros
    
    Raises:
        PersistenceError: Se houver erro na requisição
    """
    print("[PERSISTENCE] 📖 Lendo todos os registros...")
    url = f"{BASE_URL}/registros"
    resultado = _fazer_requisicao(url, metodo="GET")
    total = len(resultado) if resultado else 0
    print(f"[PERSISTENCE] 📖 Total de registros: {total}")
    return resultado if resultado is not None else []


def create_registro(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria um novo registro no servidor.
    
    Args:
        item: Dicionário com os dados do registro (sem 'id', será gerado pelo servidor)
    
    Returns:
        Dicionário com o registro criado (incluindo 'id' gerado)
    
    Raises:
        PersistenceError: Se houver erro na requisição
    """
    print(f"[PERSISTENCE] ➕ Criando registro (Mês {item.get('mes', '?')})...")
    url = f"{BASE_URL}/registros"
    resultado = _fazer_requisicao(url, metodo="POST", dados=item)
    print(f"[PERSISTENCE] ➕ Registro criado com ID: {resultado.get('id', '?')}")
    return resultado


def update_registro(registro_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
    """
    Atualiza parcialmente um registro existente.
    
    Args:
        registro_id: ID do registro a ser atualizado
        patch: Dicionário com os campos a serem atualizados
    
    Returns:
        Dicionário com o registro atualizado
    
    Raises:
        PersistenceError: Se houver erro na requisição
    """
    print(f"[PERSISTENCE] ✏️  Atualizando registro ID {registro_id}...")
    url = f"{BASE_URL}/registros/{registro_id}"
    resultado = _fazer_requisicao(url, metodo="PATCH", dados=patch)
    print(f"[PERSISTENCE] ✏️  Registro {registro_id} atualizado")
    return resultado


def delete_registro(registro_id: int) -> None:
    """
    Remove um registro do servidor.
    
    Args:
        registro_id: ID do registro a ser removido
    
    Raises:
        PersistenceError: Se houver erro na requisição
    """
    print(f"[PERSISTENCE] 🗑️  Deletando registro ID {registro_id}...")
    url = f"{BASE_URL}/registros/{registro_id}"
    _fazer_requisicao(url, metodo="DELETE")
    print(f"[PERSISTENCE] 🗑️  Registro {registro_id} deletado")


def delete_todos_registros() -> None:
    """
    Remove todos os registros do servidor.
    Faz múltiplas requisições DELETE, uma para cada registro.
    
    Raises:
        PersistenceError: Se houver erro na requisição
    """
    print("[PERSISTENCE] 🗑️  Deletando TODOS os registros...")
    registros = read_all_registros()
    total = len(registros)
    print(f"[PERSISTENCE] 🗑️  Total a deletar: {total}")
    
    for i, reg in enumerate(registros, 1):
        if "id" in reg:
            print(f"[PERSISTENCE] 🗑️  Deletando {i}/{total}...")
            delete_registro(reg["id"])
    
    print(f"[PERSISTENCE] 🗑️  Todos os {total} registros foram deletados")


def read_config() -> Dict[str, Any]:
    """
    Busca a configuração do servidor.
    
    Returns:
        Dicionário com a configuração (divida_inicial, taxa)
    
    Raises:
        PersistenceError: Se houver erro na requisição
    """
    url = f"{BASE_URL}/config"
    resultado = _fazer_requisicao(url, metodo="GET")
    
    # JSON Server retorna array, pegamos o primeiro item
    if isinstance(resultado, list) and len(resultado) > 0:
        return resultado[0]
    
    # Fallback: valores padrão
    return {"divida_inicial": 50000.0, "taxa": 0.01}


def verificar_conexao() -> bool:
    """
    Verifica se o JSON Server está acessível.
    
    Returns:
        True se conectou com sucesso, False caso contrário
    """
    if not PERSISTENCIA_ATIVA:
        print("[PERSISTENCE] ⚠️  Persistência desativada")
        return False
    
    print(f"[PERSISTENCE] 🔍 Verificando conexão com {BASE_URL}...")
    try:
        _fazer_requisicao(f"{BASE_URL}/registros", metodo="GET", timeout=2)
        print("[PERSISTENCE] ✅ Conexão estabelecida!")
        return True
    except PersistenceError as e:
        print(f"[PERSISTENCE] ❌ Falha na conexão: {e}")
        return False
