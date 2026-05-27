#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camada de persistência — 100% Python com SQLite nativo.

Anteriormente, essa camada usava HTTP (urllib) para se comunicar com um
servidor json-server rodando em Node.js. A arquitetura foi migrada para
SQLite puro, eliminando a dependência do Node.js e ganhando em velocidade,
simplicidade e robustez.

Todas as funções públicas mantêm as mesmas assinaturas da versão anterior,
garantindo que o controle_divida.py não precise de nenhuma alteração.
"""

import sqlite3
import os
import sys

# Garante que o print funciona com emojis e acentos no terminal Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from typing import List, Dict, Optional, Any

# ─────────────────────────────────────────────
# Configuração do banco de dados
# ─────────────────────────────────────────────

# O banco fica na mesma pasta deste arquivo (raiz do projeto)
_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_DIR, "dados.db")


class PersistenceError(Exception):
    """Erro genérico de persistência — mantido para compatibilidade com o código que chama essa camada."""
    pass


# ─────────────────────────────────────────────
# Inicialização do banco (cria tabelas se não existirem)
# Equivalente a uma "migration" no mundo ORM/Sequelize/Prisma
# ─────────────────────────────────────────────

def _inicializar_banco() -> None:
    """
    Cria as tabelas no banco SQLite caso ainda não existam.
    Chamada automaticamente na primeira operação — o usuário não precisa fazer nada.

    [Para devs JS]: Equivale a rodar 'prisma migrate dev' ou o CREATE TABLE
    do Sequelize na inicialização do servidor. Aqui usamos 'IF NOT EXISTS'
    para ser idempotente (pode ser chamada várias vezes sem erro).
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                mes          INTEGER,
                data         TEXT,
                data_pagamento TEXT,
                data_referencia TEXT,
                valor        REAL,
                juros        REAL,
                amort        REAL,
                saldo        REAL,
                status       TEXT,
                tipo         TEXT,
                created_at   TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id             INTEGER PRIMARY KEY,
                divida_inicial REAL,
                taxa           REAL
            )
        """)
        conn.commit()
        print(f"[PERSISTENCE] ✅ Banco SQLite inicializado em: {DB_PATH}")
    finally:
        conn.close()


# Inicializa o banco ao importar o módulo
_inicializar_banco()


# ─────────────────────────────────────────────
# Funções auxiliares internas
# ─────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    """
    Retorna uma conexão SQLite com row_factory configurada para
    devolver dicionários em vez de tuplas — igual ao comportamento
    do json-server que devolvia objetos JSON.

    [Para devs JS]: row_factory = sqlite3.Row é como fazer um .toJSON()
    automático em cada linha retornada pelo banco.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows viram dict-like, ex: row["id"]
    return conn


def _row_to_dict(row) -> Dict[str, Any]:
    """Converte uma Row do SQLite em dicionário Python puro."""
    return dict(row)


# ─────────────────────────────────────────────
# API Pública — mesmas assinaturas da versão anterior com urllib
# ─────────────────────────────────────────────

def verificar_conexao() -> bool:
    """
    Verifica se o banco de dados está acessível.

    Antes: fazia GET http://localhost:3000/registros e verificava o status HTTP.
    Agora: simplesmente tenta abrir o arquivo .db no disco.

    Returns:
        True se o banco estiver acessível, False caso contrário.
    """
    print(f"[PERSISTENCE] 🔍 Verificando banco SQLite em: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        print("[PERSISTENCE] ✅ Banco acessível!")
        return True
    except Exception as e:
        print(f"[PERSISTENCE] ❌ Erro ao acessar banco: {e}")
        return False


def read_all_registros() -> List[Dict[str, Any]]:
    """
    Busca todos os registros do banco, ordenados por id.

    Antes: GET http://localhost:3000/registros
    Agora: SELECT * FROM registros ORDER BY id

    Returns:
        Lista de dicionários com os registros.
    """
    print("[PERSISTENCE] 📖 Lendo todos os registros...")
    try:
        conn = _get_conn()
        cursor = conn.execute("SELECT * FROM registros ORDER BY id")
        rows = [_row_to_dict(row) for row in cursor.fetchall()]
        conn.close()
        print(f"[PERSISTENCE] 📖 Total de registros: {len(rows)}")
        return rows
    except Exception as e:
        raise PersistenceError(f"Erro ao ler registros: {e}")


def create_registro(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria um novo registro no banco.

    Antes: POST http://localhost:3000/registros (com body JSON)
    Agora: INSERT INTO registros VALUES (...)

    Args:
        item: Dicionário com os dados do registro.

    Returns:
        O registro criado, incluindo o 'id' gerado pelo banco.
    """
    print(f"[PERSISTENCE] ➕ Criando registro...")
    try:
        conn = _get_conn()
        cursor = conn.execute(
            """
            INSERT INTO registros
                (mes, data, data_pagamento, data_referencia,
                 valor, juros, amort, saldo, status, tipo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("mes"),
                item.get("data"),
                item.get("data_pagamento"),
                item.get("data_referencia"),
                item.get("valor"),
                item.get("juros"),
                item.get("amort"),
                item.get("saldo"),
                item.get("status"),
                item.get("tipo"),
                item.get("createdAt"),
            )
        )
        conn.commit()
        novo_id = cursor.lastrowid  # equivale ao 'id' retornado pelo json-server no POST

        # Busca o registro recém criado para devolver completo (mesmo comportamento de antes)
        row = conn.execute("SELECT * FROM registros WHERE id = ?", (novo_id,)).fetchone()
        conn.close()

        resultado = _row_to_dict(row)
        print(f"[PERSISTENCE] ✅ Registro criado com ID: {novo_id}")
        return resultado
    except Exception as e:
        raise PersistenceError(f"Erro ao criar registro: {e}")


def update_registro(registro_id: int, dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Atualiza campos de um registro existente.

    Antes: PATCH http://localhost:3000/registros/:id
    Agora: UPDATE registros SET campo=? WHERE id=?

    Args:
        registro_id: ID do registro a atualizar.
        dados: Dicionário com os campos e novos valores.

    Returns:
        O registro atualizado.
    """
    print(f"[PERSISTENCE] ✏️  Atualizando registro ID={registro_id}...")
    if not dados:
        raise PersistenceError("Nenhum campo para atualizar.")
    try:
        # Monta o SET dinamicamente com base nas chaves do dicionário 'dados'
        # Ex: {"status": "Pago"} → "SET status = ?"
        campos = ", ".join(f"{k} = ?" for k in dados.keys())
        valores = list(dados.values()) + [registro_id]

        conn = _get_conn()
        conn.execute(f"UPDATE registros SET {campos} WHERE id = ?", valores)
        conn.commit()

        row = conn.execute("SELECT * FROM registros WHERE id = ?", (registro_id,)).fetchone()
        conn.close()

        if row is None:
            raise PersistenceError(f"Registro ID={registro_id} não encontrado.")

        resultado = _row_to_dict(row)
        print(f"[PERSISTENCE] ✅ Registro ID={registro_id} atualizado.")
        return resultado
    except PersistenceError:
        raise
    except Exception as e:
        raise PersistenceError(f"Erro ao atualizar registro: {e}")


def delete_registro(registro_id: int) -> None:
    """
    Deleta um registro pelo ID.

    Antes: DELETE http://localhost:3000/registros/:id
    Agora: DELETE FROM registros WHERE id=?

    Args:
        registro_id: ID do registro a deletar.
    """
    print(f"[PERSISTENCE] 🗑️  Deletando registro ID={registro_id}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
        conn.commit()
        conn.close()
        print(f"[PERSISTENCE] ✅ Registro ID={registro_id} deletado.")
    except Exception as e:
        raise PersistenceError(f"Erro ao deletar registro: {e}")


def delete_todos_registros() -> None:
    """
    Deleta todos os registros do banco de uma só vez.

    Antes: Loop de requisições DELETE para cada ID encontrado.
    Agora: DELETE FROM registros (uma única operação SQL — muito mais rápido).
    """
    print("[PERSISTENCE] 🗑️  Deletando todos os registros...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM registros")
        conn.commit()
        conn.close()
        print("[PERSISTENCE] ✅ Todos os registros deletados.")
    except Exception as e:
        raise PersistenceError(f"Erro ao deletar registros: {e}")


def read_config() -> Optional[Dict[str, Any]]:
    """
    Lê a configuração salva no banco (dívida inicial e taxa de juros).

    Antes: GET http://localhost:3000/config
    Agora: SELECT * FROM config LIMIT 1

    Returns:
        Dicionário com a configuração ou None se não houver.
    """
    print("[PERSISTENCE] ⚙️  Lendo configuração do banco...")
    try:
        conn = _get_conn()
        row = conn.execute("SELECT * FROM config LIMIT 1").fetchone()
        conn.close()
        if row:
            return _row_to_dict(row)
        return None
    except Exception as e:
        raise PersistenceError(f"Erro ao ler configuração: {e}")
