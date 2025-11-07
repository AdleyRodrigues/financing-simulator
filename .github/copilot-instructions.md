# Copilot Instructions - Controle de Dívida

## Visão Geral do Projeto
Este é um aplicativo de controle de dívida em Tkinter com uma dívida inicial fixa de R$ 50.000,00 e taxa de juros de 1% ao mês. O usuário registra pagamentos mensais e o sistema calcula automaticamente juros, amortização e saldo restante.

## Arquitetura e Componentes Principais

### Estrutura do Projeto
- **Arquivo principal**: `controle_divida.py` - lógica da aplicação e interface Tkinter
- **Módulo de persistência**: `persistence.py` - camada de comunicação com JSON Server (urllib)
- **Diretório servidor**: `servidor/` - backend JSON Server com package.json próprio
  - `db.json` - arquivo JSON Server com registros e configuração
  - `start_server.bat` / `start_server.sh` - scripts para iniciar o servidor
- **Classe principal**: `ControleDividaApp` - herda de `tk.Tk` e gerencia toda a interface
- **Estado em memória**: Dados armazenados em `self.registros` (lista de dicts) com sincronização opcional

### Lógica Financeira Central
```python
# Fórmula aplicada a cada pagamento:
juros = saldo_anterior * 0.01
amortizacao = valor_pago - juros
novo_saldo = saldo_anterior - amortizacao
```

**Comportamento especial**: Se o pagamento exceder o saldo devedor + juros, o sistema ajusta automaticamente para quitar a dívida.

## Padrões e Convenções Específicas

### Formatação Monetária
Use a função `format_brl()` que implementa formatação brasileira sem dependências:
- Converte `12345.67` para `"R$ 12.345,67"`
- Não depende de locale do sistema

### Parsing de Entrada do Usuário
- **Valores**: `_parse_valor()` aceita formatos com "R$", vírgulas e pontos
- **Datas**: `_parse_data()` aceita "dd/mm/aaaa" ou "dd/mm/aa" (assume século 21)

### Gestão de Estado
- Estado mantido em `self.registros` (lista de dicionários)
- Cada registro local contém campo opcional `server_id` para rastreamento
- Campos agregados: `self.total_pago` e `self.saldo_restante`
- **Importante**: Use `_recalcular_agregado_e_table()` após remoções para evitar erros de arredondamento

### Persistência (Modo Online/Offline)
- **Módulo**: `persistence.py` usa apenas urllib (sem dependências externas)
- **Endpoints**: JSON Server em `http://localhost:3000` com timeout de 3s
- **Detecção automática**: Aplicação verifica servidor ao iniciar com `_verificar_servidor()`
- **Operações**: CRUD completo - `create_registro()`, `read_all_registros()`, `update_registro()`, `delete_registro()`
- **Sincronização**: Cada operação (registrar, alterar status, desfazer, reiniciar) tenta salvar no servidor
- **Fallback gracioso**: Se servidor indisponível, exibe aviso e continua em modo offline
- **Indicador visual**: Header mostra "🟢 Online" ou "🔴 Offline"

## Interface do Usuário

### Componentes Tkinter
- **Formulário**: Entrada de valor, data (sugerida automaticamente) e status
- **Tabela**: Treeview com 7 colunas (Mês, Data, Valor Pago, Juros, Amortização, Saldo, Status)
- **Resumos**: Total pago e saldo restante em tempo real

### Fluxo de Interação
1. Sistema sugere próxima data (mês seguinte da última entrada)
2. Usuário informa valor e confirma/edita data
3. Cálculos automáticos atualizam tabela e resumos
4. Foco retorna ao campo de valor para próxima entrada

## Funcionalidades Especiais

### Status de Pagamento
- Status "Pago"/"Pendente" é informativo - não altera cálculos financeiros
- Pode ser alterado via botão "Alternar Status" com seleção na tabela

### Operações de Desfazer
- **Desfazer último**: Remove último registro e recalcula tudo
- **Reiniciar**: Limpa todos os dados após confirmação

## Desenvolvimento e Debugging

### Executar o Aplicativo

**Modo Offline** (sem persistência):
```bash
python controle_divida.py
```

**Modo Online** (com persistência):
```bash
# Terminal 1: Iniciar JSON Server
cd servidor
pnpm install  # ou: npm install (apenas primeira vez)
pnpm start    # ou: ./start_server.bat (Windows) / ./start_server.sh (Linux/Mac)

# Terminal 2: Executar aplicação (voltar para raiz)
cd ..
python controle_divida.py
```

### Pontos de Atenção
- **Persistência condicional**: Dados salvos apenas se JSON Server estiver disponível
- **Arredondamento**: 2 casas decimais em todos os cálculos financeiros
- **Tratamento de erro**: Valores/datas inválidas geram messageboxes
- **Timeout de rede**: 3 segundos para operações HTTP
- **Sincronização**: Cada registro local guarda `server_id` para rastreamento
- **Ajuste de tema**: Tkinter tenta vista → clam → padrão

### Testagem Manual
- Testar pagamentos que excedem saldo devedor
- Verificar cálculos com valores decimais
- Validar formatação de datas e valores brasileiros
- Confirmar recálculos após operações de desfazer