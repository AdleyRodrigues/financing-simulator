# Controle de Dívida

Aplicação desktop para controlar pagamento de dívida pessoal com juros configuráveis.

**Stack:** Python 3 + Tkinter + JSON Server (Node.js)

## ⚙️ Configuração

Edite o arquivo `config.json` para ajustar os valores:

```json
{
  "divida_inicial": 50000.00,
  "taxa_juros": 0.01
}
```

- `divida_inicial`: Valor inicial da dívida em reais
- `taxa_juros`: Taxa de juros mensal (0.01 = 1% ao mês, 0.02 = 2% ao mês, etc.)

O arquivo é criado automaticamente na primeira execução se não existir.

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
├── config.json           # Configurações (dívida inicial, taxa)
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
