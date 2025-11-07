# Controle de Dívida

Aplicação desktop para controlar pagamento de dívida pessoal com juros de 1% ao mês.

**Stack:** Python 3 + Tkinter + JSON Server (Node.js)

## 🚀 Uso

### Modo Offline (dados não salvos)
```bash
python controle_divida.py
```

### Modo Online (com persistência)
```bash
# Terminal 1: Servidor
cd servidor
pnpm install  # primeira vez apenas
pnpm start

# Terminal 2: Aplicação
python controle_divida.py
```

Indicador no header:
- 🟢 **Online** - dados salvos no servidor
- 🔴 **Offline** - dados apenas em memória

## 📁 Estrutura

```
ControleDivida/
├── controle_divida.py    # Aplicação principal
├── persistence.py         # Camada de persistência
├── test_persistence.py    # Testes
├── servidor/              # Backend
│   ├── db.json           # Dados
│   ├── package.json
│   └── start_server.*
└── README.md
```

## 🧮 Cálculo

```python
juros = saldo_anterior * 0.01
amortizacao = valor_pago - juros
novo_saldo = saldo_anterior - amortizacao
```

## 🛠️ Requisitos

- Python 3.6+
- tkcalendar (`pip install tkcalendar`)
- Node.js (para modo online)
