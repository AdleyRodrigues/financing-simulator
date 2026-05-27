# 💰 Controle de Dívida (Simulador Financeiro)

Uma aplicação desktop (100% Python + SQLite) desenvolvida para simular, projetar e gerenciar o pagamento de uma dívida pessoal através do cálculo matemático de juros compostos e amortização de saldo devedor.

Construído com foco em extrema velocidade de execução, uso leve de recursos (sem servidores rodando em background) e separação de responsabilidades limpa entre interface gráfica e persistência de dados.

## 🚀 Sobre o Projeto

O **Controle de Dívida** permite ao usuário acompanhar a evolução da sua dívida mês a mês. 
A cada lançamento efetuado, o sistema calcula dinamicamente:
1. Os **Juros** incidentes (ex: 1% ao mês) sobre o Saldo Devedor do mês anterior.
2. A **Amortização** (Valor Pago - Juros).
3. O **Novo Saldo Devedor**.

O grande diferencial matemático é a capacidade de registrar meses de **Inadimplência (Sem pagamento)**, o que aciona o cálculo de *juros compostos* (juros sobre juros), elevando o saldo devedor total, simulando perfeitamente a realidade de financiamentos.

## 🛠️ Stack Tecnológica & Arquitetura

Este projeto foi **recém-migrado** para uma arquitetura 100% nativa Python, abolindo a dependência anterior de Node.js. 

Para detalhes profundos sobre como os componentes se comunicam e os **motivos de negócio que nos levaram a refatorar a aplicação**, consulte a documentação arquitetural nas pastas de diagrama abaixo:
* 🗺️ [Diagrama da Arquitetura Atual (V2) — Python + SQLite](diagramas/arquitetura-atual.md)
* 🛑 [Diagrama da Arquitetura Legado (V1) — Por que abandonamos o Node.js?](diagramas/arquitetura-legado.md)

**A Stack Atual (V2):**
* **Frontend (Interface Gráfica):** Desenvolvido em **Python 3** usando `Tkinter` e `tkcalendar`. Toda a renderização, lógica matemática, atualização reativa de estado da UI e controle de fluxo estão concentrados neste módulo principal Desktop.
* **Backend (Persistência Nativa):** Em vez de HTTP ou APIs REST locais, o módulo `persistence.py` acessa diretamente o disco utilizando o motor relacional embutido **`sqlite3`**, garantindo transações ACID e velocidade instantânea nas gravações.

## 💻 Funcionalidades em Destaque

* **Tabela Dinâmica de Histórico:** Interface em planilha que detalha o histórico, sinalizada por cores (pagamentos em atraso, meses em aberto, etc).
* **Duplo Sistema de Datas:** Suporte para diferenciar a "Data de Referência" (vencimento do mês) vs "Data de Pagamento" (dia em que a transação ocorreu de fato).
* **Previsão Estimada:** Calcula e estima na tela os juros correntes que estão aguardando pagamento se houverem lacunas ou dias em aberto no mês.
* **Automação de Inicialização (`iniciar.bat`):** Script inteligente que identifica e valida o ambiente (Python), garantindo a inicialização da aplicação inteiramente limpa e silenciosa em background.

## ⚙️ Como Executar o Projeto

*Nota: Por questões de segurança, os arquivos contendo valores originais da dívida e o histórico do banco de dados local (`dados.db` e `config.json`) estão protegidos no `.gitignore` e não fazem parte deste repositório público.*

### Pré-requisitos
- **Python 3.6+** (O SQLite3 já é embutido na linguagem)

### Rodando a Aplicação (Windows)
Apenas execute o arquivo `iniciar.bat`.
O script checará a existência do Python, verificará a integridade de sintaxe do código e inicializará a interface gráfica em modo oculto (sem janela de terminal), encerrando-se na mesma hora.

### Execução Manual pelo Terminal
```bash
python controle_divida.py
```
*(O banco de dados `.db` se auto-criará no primeiro instante em que uma inserção for demandada, sem necessidade de migrations manuais).*

## 📁 Estrutura de Diretórios
```text
financing-simulator/
├── controle_divida.py     # UI Principal, Lógica de Negócio e Estado Reativo
├── persistence.py         # Módulo de Banco de Dados local nativo (SQLite)
├── iniciar.bat            # Script de inicialização rápida (Windows)
└── diagramas/             # Documentação Arquitetural e Decisões de Engenharia
    ├── arquitetura-atual.md
    └── arquitetura-legado.md
```
