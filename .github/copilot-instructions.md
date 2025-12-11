# Copilot Instructions - Controle de Dívida

## 🇧🇷 Idioma
**IMPORTANTE**: Sempre responda em português brasileiro. Toda comunicação, explicações, comentários e documentação devem ser em português.

## Visão Geral do Projeto
Este é um aplicativo desktop para controle de dívida pessoal desenvolvido em Python + Tkinter com persistência opcional via JSON Server. A aplicação simula um financiamento de R$ 50.000,00 com juros de 1% ao mês, permitindo ao usuário registrar pagamentos mensais e acompanhar a evolução da dívida.

## Arquitetura e Componentes

### Estrutura Principal
```
financing-simulator/
├── controle_divida.py     # App principal (Tkinter)
├── config.json            # Configurações (dívida inicial, taxa)
├── persistence.py         # Camada de persistência (urllib)
├── test_persistence.py    # Testes da camada HTTP
├── servidor/              # Backend JSON Server
│   ├── db.json           # Dados + configuração
│   ├── package.json      # Dependências Node.js
│   ├── start_server.bat  # Script Windows
│   └── start_server.sh   # Script Unix/Linux
```

### Classe Central: `ControleDividaApp`
- Herda de `tk.Tk` e gerencia toda a interface
- Estado em memória: `self.registros` (lista de dicts)
- Agregados calculados: `self.total_pago` e `self.saldo_restante`
- Modo híbrido: online (com servidor) ou offline (apenas memória)

### Lógica Financeira Configurável
```python
# Aplicada a cada pagamento:
juros = saldo_anterior * self.taxa  # Taxa definida em config.json
amortizacao = valor_pago - juros
novo_saldo = saldo_anterior - amortizacao
```

**Configuração**: Valores carregados de `config.json`:
- `divida_inicial`: Valor inicial da dívida (padrão: R$ 50.000,00)
- `taxa_juros`: Taxa mensal em decimal (padrão: 0.01 = 1%)

**Auto-ajuste**: Se pagamento > saldo + juros, ajusta para quitar automaticamente.

## Padrões de Código Específicos

### Formatação Brasileira sem Dependências
- `format_brl(12345.67)` → `"R$ 12.345,67"`
- Implementação manual (não usa locale)

### Parsing Flexível de Entrada
- **Valores**: `_parse_valor()` aceita "2500", "2500,50", "R$ 2.500,50"
- **Datas**: `_parse_data()` aceita "dd/mm/yyyy" e "dd/mm/yy" (assume 20xx)
- **Máscaras**: Aplicação automática em tempo real via callbacks

### Estado Sincronizado
- Cada registro local pode ter `server_id` para rastreamento
- **CRÍTICO**: Use `_recalcular_agregado_e_table()` após remoções (evita erros de float)
- Recalcula toda a sequência financeira do zero

## Persistência Condicional

### Detecção Automática de Servidor
- `_verificar_servidor()` testa conexão ao iniciar
- Indicador visual: "🟢 Online" ou "🔴 Offline" no header
- Fallback gracioso: continua funcionando sem servidor

### Operações HTTP (persistence.py)
- **Base**: `http://localhost:3000` (JSON Server)
- **Timeout**: 3 segundos para todas as operações
- **Logging**: Prefixo `[PERSISTENCE]` em todas as operações
- **Endpoints**: `/registros` (CRUD) e `/config` (configuração)

### Sincronização de Dados
- Cada operação (criar, alterar, deletar) tenta salvar no servidor
- Se falhar, exibe warning mas continua funcionando
- Carregamento inicial: `_carregar_registros_iniciais()` sincroniza estado

## Fluxo de Interação Típico

### Entrada de Dados
1. Sistema sugere próxima data (mês seguinte do último registro)
2. Campo de valor recebe foco automático
3. Calendário tkcalendar ou entrada manual de data
4. Status "Pago"/"Pendente" (informativo, não afeta cálculos)

### Comportamentos Especiais
- **Auto-quitação**: Pagamentos excessivos são ajustados
- **Data sugerida**: Atualizada automaticamente para próximo mês
- **Recálculo completo**: Operações de desfazer recalculam tudo

## Comandos de Desenvolvimento

### Execução Modo Offline
```bash
python controle_divida.py
```

### Execução Modo Online
```powershell
# Terminal 1: Servidor
cd servidor
pnpm install  # primeira vez
pnpm start

# Terminal 2: Aplicação
python controle_divida.py
```

### Scripts de Servidor
- Windows: `servidor/start_server.bat`
- Unix/Linux: `servidor/start_server.sh`
- **Auto-detecção**: pnpm → yarn → npm
- **Portas**: 3000 (padrão), scripts suportam customização

### Testagem
```bash
python test_persistence.py  # Testa operações HTTP
```

## Dependências e Instalação

### Python
- **Obrigatório**: Tkinter (geralmente incluso)
- **Opcional**: tkcalendar (auto-instalação tentada)
- **Fallback**: Campo de data manual se tkcalendar falhar

### Node.js (apenas modo online)
- JSON Server 0.17.4
- Gerenciadores suportados: pnpm, yarn, npm
- Scripts de início detectam automaticamente

### Configuração Inicial
- `config.json` é criado automaticamente na primeira execução
- Edite `config.json` para alterar dívida inicial ou taxa de juros
- Mudanças exigem reinicialização da aplicação

## Pontos Críticos para Debugging

### Erros Comuns
- **Arredondamento**: Sempre 2 casas decimais nos cálculos
- **Timeout HTTP**: 3s limite pode causar falsos offline
- **Recálculo**: Use `_recalcular_agregado_e_table()` após mudanças na lista
- **server_id**: Campo opcional que conecta registro local ao servidor

### Validações
- Valores devem ser > 0
- Datas em formato brasileiro válido
- Conexão servidor testada a cada operação
- Auto-ajuste de pagamentos excessivos