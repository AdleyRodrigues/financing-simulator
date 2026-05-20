# 💰 Controle de Dívida (Simulador Financeiro)

Uma aplicação desktop híbrida (Python + Node.js) desenvolvida para simular, projetar e gerenciar o pagamento de uma dívida pessoal através do cálculo matemático de juros compostos e amortização de saldo devedor.

Construído com foco em resiliência offline/online e separação de responsabilidades entre interface gráfica e persistência de dados.

## 🚀 Sobre o Projeto

O **Controle de Dívida** permite ao usuário acompanhar a evolução da sua dívida mês a mês. 
A cada lançamento efetuado, o sistema calcula dinamicamente:
1. Os **Juros** incidentes (ex: 1% ao mês) sobre o Saldo Devedor do mês anterior.
2. A **Amortização** (Valor Pago - Juros).
3. O **Novo Saldo Devedor**.

O grande diferencial matemático é a capacidade de registrar meses de **Inadimplência (Sem pagamento)**, o que aciona o cálculo de *juros compostos* (juros sobre juros), elevando o saldo devedor total, simulando perfeitamente a realidade de financiamentos.

## 🛠️ Stack Tecnológica & Arquitetura

O projeto adota uma arquitetura híbrida dividida em duas camadas (Cliente e Servidor local):

* **Frontend (Interface Gráfica):** Desenvolvido em **Python 3** usando `Tkinter` e `tkcalendar`. Toda a renderização, lógica matemática, atualização reativa de estado da UI e controle de fluxo estão concentrados neste módulo principal Desktop.
* **Backend (Camada de Dados):** Desenvolvido utilizando **Node.js** com `json-server`. Simula uma API RESTful (`GET`, `POST`, `PATCH`, `DELETE`) para garantir persistência de dados fora da memória local.
* **Comunicação Resiliente:** O módulo `persistence.py` faz a ponte de comunicação HTTP entre o Python e a API sem usar bibliotecas externas (construído com a nativa `urllib`), com tratamento completo para queda de conexão (fallback automático e transparente para "Modo Offline" na tela).

## 💻 Funcionalidades em Destaque

* **Tabela Dinâmica de Histórico:** Interface em planilha que detalha o histórico, sinalizada por cores (pagamentos em atraso, meses em aberto, etc).
* **Duplo Sistema de Datas:** Suporte para diferenciar a "Data de Referência" (vencimento do mês) vs "Data de Pagamento" (dia em que a transação ocorreu de fato).
* **Previsão Estimada:** Calcula e estima na tela os juros correntes que estão aguardando pagamento se houverem lacunas ou dias em aberto no mês.
* **Automação de Inicialização (`iniciar.bat`):** Script inteligente que identifica o ambiente, instala as dependências do Node e do Python em silêncio, inicializa o servidor JSON em background e sobe a tela da UI em paralelo (com encerramento automático do serviço back-end ao fechar a janela).

## ⚙️ Como Executar o Projeto

*Nota: Por questões de segurança, os arquivos contendo valores originais da dívida e histórico local do banco de dados (`db.json` e `config.json`) estão protegidos no `.gitignore` e não fazem parte deste repositório público.*

### Pré-requisitos
- **Python 3.6+**
- **Node.js** (Para o módulo de banco de dados REST)

### Rodando a Aplicação (Windows)
Apenas execute o arquivo `iniciar.bat`.
O script fará automaticamente a checagem dos requisitos, o setup do servidor Node.js em background e instanciará a interface gráfica Python.

### Execução Manual
**1. Inicializando a API:**
```bash
cd servidor
npm install
npm start
```
**2. Inicializando o App Desktop (Em outro terminal):**
```bash
python controle_divida.py
```

## 📁 Estrutura de Diretórios
```text
financing-simulator/
├── controle_divida.py     # UI Principal e Core Rules
├── persistence.py         # API Client HTTP wrapper
├── test_persistence.py    # Testes unitários do CRUD e rede
├── servidor/              # Diretório do Backend (Node API)
│   ├── package.json
│   └── start_server.bat
└── iniciar.bat            # Automação de ambiente
```
