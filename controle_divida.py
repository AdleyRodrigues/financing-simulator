#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini app Tkinter: Controle de Dívida com Juros (1% a.m.)
- Dívida inicial: R$ 50.000,00
- Juros: 1% ao mês sobre o saldo devedor do mês anterior
- Usuário registra, mês a mês (quantidade indefinida), quanto deseja pagar
- Para cada mês:
    juros = saldo_anterior * 0.01
    amortização = valor_pago - juros
    novo_saldo = saldo_anterior - amortização
- Histórico em tabela: Mês, Data, Valor Pago, Juros, Amortização, Dívida Restante, Status
- Status: "Pago" (padrão) ou "Pendente" (informativo; não altera a lógica de cálculo)
- Armazenamento apenas em memória
- Sem dependências além de Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from calendar import monthrange

# Importar calendário
try:
    from tkcalendar import DateEntry
    CALENDARIO_DISPONIVEL = True
except ImportError:
    CALENDARIO_DISPONIVEL = False
    print("⚠️  tkcalendar não encontrado. Instalando...")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tkcalendar"])
        from tkcalendar import DateEntry
        CALENDARIO_DISPONIVEL = True
        print("✅ tkcalendar instalado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao instalar tkcalendar: {e}")
        print("   Continuando com entrada manual de data.")

# Importar módulo de persistência
try:
    import persistence
    PERSISTENCIA_DISPONIVEL = True
except ImportError:
    PERSISTENCIA_DISPONIVEL = False
    print("⚠️  Módulo persistence.py não encontrado. Modo offline ativado.")


def carregar_configuracao():
    """Carrega configurações do arquivo config.json."""
    import os
    import json
    
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    # Valores padrão
    config_padrao = {
        "divida_inicial": 50000.00,
        "taxa_juros": 0.01
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ Configuração carregada de {config_path}")
                return {
                    "divida_inicial": float(config.get("divida_inicial", config_padrao["divida_inicial"])),
                    "taxa_juros": float(config.get("taxa_juros", config_padrao["taxa_juros"]))
                }
        else:
            print(f"⚠️  Arquivo config.json não encontrado. Usando valores padrão.")
            # Criar arquivo de configuração padrão
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "divida_inicial": config_padrao["divida_inicial"],
                    "taxa_juros": config_padrao["taxa_juros"],
                    "comentarios": {
                        "divida_inicial": "Valor inicial da dívida em reais",
                        "taxa_juros": "Taxa de juros mensal (0.01 = 1% ao mês)"
                    }
                }, f, indent=2, ensure_ascii=False)
            print(f"✅ Arquivo config.json criado com valores padrão")
            return config_padrao
    except Exception as e:
        print(f"⚠️  Erro ao carregar config.json: {e}. Usando valores padrão.")
        return config_padrao


# Carregar configuração
CONFIG = carregar_configuracao()
DIVIDA_INICIAL = CONFIG["divida_inicial"]
TAXA_JUROS = CONFIG["taxa_juros"]


def format_brl(valor: float) -> str:
    """Formata número float no padrão brasileiro simples (R$ 1.234,56) sem depender de locale."""
    s = f"{valor:,.2f}"  # ex: 12,345.67 (padrão EUA)
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def next_month(d: date) -> date:
    """Retorna a mesma 'day' do mês seguinte, ajustando para o último dia caso necessário."""
    year = d.year + (1 if d.month == 12 else 0)
    month = 1 if d.month == 12 else d.month + 1
    day = d.day
    last_day = monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


class ControleDividaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Controle de Dívida - Juros 1% a.m.")
        self.geometry("880x560")
        self.resizable(True, True)  # Permite maximizar a janela

        # Estado em memória
        self.divida_inicial = DIVIDA_INICIAL
        self.taxa = TAXA_JUROS
        self.registros = []  # lista de dicts com as colunas
        self.total_pago = 0.0
        self.saldo_restante = self.divida_inicial
        
        # Controle de persistência
        self.modo_online = False
        self._verificar_servidor()

        # Próxima data sugerida (começa hoje; a cada registro, sugere mês seguinte)
        self.data_sugerida = date.today()

        # Variáveis de UI
        self.var_valor = tk.StringVar(value="")
        self.var_data = tk.StringVar(value=self.data_sugerida.strftime("%d/%m/%Y"))
        self.var_status = tk.StringVar(value="Pago")

        print("🎨 Resumos iniciais:")
        print(f"   Total pago: {format_brl(self.total_pago)}")
        print(f"   Dívida restante: {format_brl(self.saldo_restante)}")

        # Layout principal
        self._build_header()
        self._build_form()
        self._build_table()
        self._build_footer()
        
        # Carregar dados do servidor (se disponível)
        self._carregar_registros_iniciais()

        self.entry_valor.focus_set()

    # ---------- Construção de UI ----------
    def _build_header(self):
        header = ttk.Frame(self, padding=(12, 12, 12, 8))
        header.pack(fill="x")

        taxa_percentual = self.taxa * 100
        ttk.Label(header, text=f"Controle de Dívida com Juros ({taxa_percentual:.1f}% a.m.)", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        
        # Indicador de modo (online/offline)
        modo_texto = "🟢 Online" if self.modo_online else "🔴 Offline"
        sub_texto = f"Dívida inicial: {format_brl(self.divida_inicial)}   •   Juros: {taxa_percentual:.1f}% ao mês   •   {modo_texto}"
        
        sub = ttk.Label(
            header,
            text=sub_texto,
            font=("Segoe UI", 10),
        )
        sub.pack(anchor="w", pady=(2, 0))

    def _build_form(self):
        form = ttk.Frame(self, padding=(12, 6, 12, 6))
        form.pack(fill="x")

        # Valor - entrada direta sem máscara
        ttk.Label(form, text="Valor pago no mês (R$):").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="(Ex: 2500 ou 2500,50)", font=("Segoe UI", 8), foreground="gray").grid(row=0, column=0, sticky="w", padx=(130, 0))
        self.entry_valor = ttk.Entry(form, width=16, textvariable=self.var_valor)
        self.entry_valor.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Data com calendário
        ttk.Label(form, text="Data:").grid(row=0, column=1, sticky="w", padx=(12, 0))
        
        if CALENDARIO_DISPONIVEL:
            # Widget de calendário
            self.date_picker = DateEntry(
                form,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                locale='pt_BR',
                firstweekday='sunday'
            )
            self.date_picker.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(2, 0))
            # Definir data sugerida
            self.date_picker.set_date(self.data_sugerida)
        else:
            # Fallback: entrada manual
            self.entry_data = ttk.Entry(form, width=14, textvariable=self.var_data)
            self.entry_data.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(2, 0))
            self.entry_data.bind('<KeyRelease>', self._aplicar_mascara_data)

        # Status
        ttk.Label(form, text="Status:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.combo_status = ttk.Combobox(form, width=12, state="readonly", values=["Pago", "Pendente"], textvariable=self.var_status)
        self.combo_status.grid(row=1, column=2, sticky="w", padx=(12, 0))
        self.combo_status.current(0)

        # Botão registrar
        self.btn_registrar = ttk.Button(form, text="Registrar Pagamento", command=self.registrar_pagamento)
        self.btn_registrar.grid(row=1, column=3, padx=(12, 0))

        # Info: Total Pago + ações
        info = ttk.Frame(self, padding=(12, 8, 12, 0))
        info.pack(fill="x", padx=12, pady=(6, 0))

        caixa_total = ttk.Frame(info)
        caixa_total.pack(side="left")
        ttk.Label(caixa_total, text="Total Pago", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        bg = self.cget("background")
        self.label_total = tk.Label(
            caixa_total,
            text=format_brl(self.total_pago),
            font=("Segoe UI", 14, "bold"),
            fg="#2E7D32",
            bg=bg,
        )
        self.label_total.pack(anchor="w")

        caixa_acoes = ttk.Frame(info)
        caixa_acoes.pack(side="right")
        self.btn_limpar = ttk.Button(caixa_acoes, text="Limpar Histórico", command=self.limpar_historico)
        self.btn_limpar.pack(side="right", padx=(0, 8))

    def _build_table(self):
        bloco = ttk.Frame(self, padding=(12, 4, 12, 8))
        bloco.pack(fill="both", expand=True)

        ttk.Label(bloco, text="Histórico de Pagamentos", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

        # Configurar estilo da tabela com linhas visíveis
        style = ttk.Style()
        style.configure("Treeview", 
                       rowheight=25,
                       borderwidth=1,
                       relief="solid")
        style.configure("Treeview.Heading",
                       font=("Segoe UI", 9, "bold"),
                       background="#E0E0E0",
                       borderwidth=1,
                       relief="raised")
        style.map("Treeview.Heading",
                 background=[("active", "#D0D0D0")])
        
        # Cores alternadas para as linhas
        self.tabela_tag_config = True
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF")

        cols = ("mes", "data", "valor", "juros", "amort", "saldo", "status")
        self.tabela = ttk.Treeview(bloco, columns=cols, show="headings", height=16)
        self.tabela.heading("mes", text="Mês")
        self.tabela.heading("data", text="Data")
        self.tabela.heading("valor", text="Valor Pago")
        self.tabela.heading("juros", text="Juros")
        self.tabela.heading("amort", text="Amortização")
        self.tabela.heading("saldo", text="Dívida Restante")
        self.tabela.heading("status", text="Status")

        self.tabela.column("mes", width=50, anchor="center")
        self.tabela.column("data", width=90, anchor="center")
        self.tabela.column("valor", width=110, anchor="center")
        self.tabela.column("juros", width=110, anchor="center")
        self.tabela.column("amort", width=120, anchor="center")
        self.tabela.column("saldo", width=130, anchor="center")
        self.tabela.column("status", width=80, anchor="center")
        
        # Configurar tags para linhas alternadas
        self.tabela.tag_configure("oddrow", background="#F5F5F5")
        self.tabela.tag_configure("evenrow", background="#FFFFFF")

        self.tabela.pack(fill="both", expand=True)

        # Scrollbar vertical
        scroll_y = ttk.Scrollbar(bloco, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")

    def _build_footer(self):
        rodape = ttk.Frame(self, padding=(12, 8, 12, 12))
        rodape.pack(side="bottom", fill="x")

        # Botões à esquerda
        self.btn_toggle = ttk.Button(rodape, text="Alternar Status", command=self.alternar_status_selecao)
        self.btn_toggle.pack(side="left")

        self.btn_undo = ttk.Button(rodape, text="Desfazer Último", command=self.desfazer_ultimo)
        self.btn_undo.pack(side="left", padx=(8, 0))

        # Botão à direita
        self.btn_reset = ttk.Button(rodape, text="Reiniciar", command=self.reiniciar)
        self.btn_reset.pack(side="right", padx=(0, 8))

    # ---------- Persistência ----------
    def _verificar_servidor(self):
        """Verifica se o JSON Server está acessível."""
        if not PERSISTENCIA_DISPONIVEL:
            self.modo_online = False
            return
        
        if persistence.verificar_conexao():
            self.modo_online = True
            print("✅ Conectado ao JSON Server")
            
            # Tentar carregar configuração do servidor
            try:
                config = persistence.read_config()
                if config:
                    self.divida_inicial = float(config.get("divida_inicial", DIVIDA_INICIAL))
                    self.taxa = float(config.get("taxa", TAXA_JUROS))
                    self.saldo_restante = self.divida_inicial
            except Exception as e:
                print(f"⚠️  Erro ao carregar config: {e}")
        else:
            self.modo_online = False
            print("⚠️  JSON Server não acessível. Modo offline ativado.")
    
    def _carregar_registros_iniciais(self):
        """Carrega registros existentes do servidor ao iniciar."""
        if not self.modo_online:
            return
        
        try:
            registros_servidor = persistence.read_all_registros()
            
            if not registros_servidor:
                return
            
            # Ordenar por id para garantir ordem cronológica
            registros_servidor.sort(key=lambda r: r.get("id", 0))
            
            # Processar cada registro
            for reg_servidor in registros_servidor:
                # Converter para formato local (sem 'id' e 'createdAt')
                reg_local = {
                    "mes": reg_servidor.get("mes", len(self.registros) + 1),
                    "data": reg_servidor.get("data", ""),
                    "valor": float(reg_servidor.get("valor", 0.0)),
                    "juros": float(reg_servidor.get("juros", 0.0)),
                    "amort": float(reg_servidor.get("amort", 0.0)),
                    "saldo": float(reg_servidor.get("saldo", 0.0)),
                    "status": reg_servidor.get("status", "Pago"),
                    "server_id": reg_servidor.get("id")  # Guardar ID do servidor
                }
                
                self.registros.append(reg_local)
                self._adiciona_na_tabela(reg_local)
            
            # Recalcular agregados
            if self.registros:
                self._recalcular_agregado_e_table()
                
                # Atualizar data sugerida para o próximo mês
                ultima_data_str = self.registros[-1]["data"]
                try:
                    d, m, a = ultima_data_str.split("/")
                    ultima_data = date(int(a), int(m), int(d))
                    self.data_sugerida = next_month(ultima_data)
                    
                    if CALENDARIO_DISPONIVEL:
                        self.date_picker.set_date(self.data_sugerida)
                    else:
                        self.var_data.set(self.data_sugerida.strftime("%d/%m/%Y"))
                except Exception:
                    pass
            
            print(f"✅ Carregados {len(self.registros)} registros do servidor")
            
        except Exception as e:
            print(f"⚠️  Erro ao carregar registros: {e}")
            messagebox.showwarning(
                "Aviso",
                f"Erro ao carregar dados do servidor:\n{e}\n\nContinuando em modo offline."
            )
            self.modo_online = False

    # ---------- Máscaras de Input ----------
    
    def _aplicar_mascara_data(self, event):
        """Aplica máscara de data (dd/mm/aaaa)."""
        # Ignora teclas especiais
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab'):
            return
        
        texto = self.var_data.get()
        
        # Remove tudo que não é dígito
        apenas_numeros = ''.join(c for c in texto if c.isdigit())
        
        if not apenas_numeros:
            return
        
        # Limita a 8 dígitos (ddmmaaaa)
        apenas_numeros = apenas_numeros[:8]
        
        # Aplica a máscara
        formatado = apenas_numeros
        if len(apenas_numeros) > 2:
            formatado = apenas_numeros[:2] + '/' + apenas_numeros[2:]
        if len(apenas_numeros) > 4:
            formatado = apenas_numeros[:2] + '/' + apenas_numeros[2:4] + '/' + apenas_numeros[4:]
        
        # Atualiza o campo
        self.var_data.set(formatado)
        
        # Reposiciona cursor no final
        self.entry_data.icursor(tk.END)

    # ---------- Lógica ----------
    def _parse_valor(self, texto: str) -> float:
        """
        Aceita formatos:
        - 2500 (inteiro)
        - 2500.50 ou 2500,50 (decimal)
        - R$ 2.500,50 (formatado)
        - 2.500,50 (com separador de milhar)
        """
        texto = texto.strip()
        
        if not texto:
            raise ValueError("Informe um valor.")
        
        # Remove R$, espaços
        t = texto.replace("R$", "").replace(" ", "").strip()
        
        # Se ficou vazio, erro
        if not t:
            raise ValueError("Informe um valor.")
        
        # Remove separador de milhar '.' e troca ',' por '.' para decimal
        # Exemplo: "2.500,50" -> "2500.50"
        t = t.replace(".", "").replace(",", ".")
        
        try:
            valor = float(t)
            if valor <= 0:
                raise ValueError("O valor deve ser maior que zero.")
            return valor
        except ValueError:
            raise ValueError("Valor inválido. Use formato: 2500 ou 2500,50")

    def _parse_data(self, texto: str) -> date:
        texto = texto.strip()
        if not texto:
            return self.data_sugerida
        # formatos aceitos: dd/mm/aaaa ou dd/mm/aa
        try:
            d, m, a = texto.split("/")
            d, m, a = int(d), int(m), int(a)
            if a < 100:
                a = 2000 + a  # suposição simples
            return date(a, m, d)
        except Exception:
            raise ValueError("Data inválida. Use dd/mm/aaaa.")

    def registrar_pagamento(self):
        print("\n" + "🎯 INICIANDO REGISTRO DE PAGAMENTO " + "="*30)
        
        # Pegar valor diretamente do widget Entry
        valor_digitado = self.entry_valor.get()
        print(f"📝 Valor do Entry widget: '{valor_digitado}'")
        print(f"📝 Valor da StringVar: '{self.var_valor.get()}'")
        
        # Validar e parse do valor
        try:
            valor_pago = self._parse_valor(valor_digitado)
            print(f"✅ Valor parseado: {valor_pago}")
        except ValueError as e:
            print(f"❌ Erro no parse do valor: {e}")
            messagebox.showerror("Erro", str(e))
            self.entry_valor.focus_set()
            return

        # Obter data do calendário ou entrada manual
        print(f"📅 Calendário disponível: {CALENDARIO_DISPONIVEL}")
        try:
            if CALENDARIO_DISPONIVEL:
                data_pag = self.date_picker.get_date()
                print(f"📅 Data do calendário: {data_pag}")
            else:
                campo_data = self.var_data.get()
                print(f"📅 Campo data: '{campo_data}'")
                data_pag = self._parse_data(campo_data)
                print(f"📅 Data parseada: {data_pag}")
        except ValueError as e:
            print(f"❌ Erro no parse da data: {e}")
            messagebox.showerror("Erro", str(e))
            return

        status = self.var_status.get() or "Pago"
        print(f"📌 Status: {status}")

        if self.saldo_restante <= 0:
            messagebox.showinfo("Concluído", "A dívida já foi quitada!")
            return

        # Cálculo do mês
        saldo_anterior = self.saldo_restante
        juros = round(saldo_anterior * self.taxa, 2)
        amortizacao = round(valor_pago - juros, 2)
        novo_saldo = round(saldo_anterior - amortizacao, 2)

        # Se pagamento exceder o saldo devedor + juros, ajusta para quitar
        if novo_saldo < 0:
            # Ajusta amortização e valor pago efetivo para zerar saldo
            amortizacao += novo_saldo  # novo_saldo é negativo
            valor_pago += novo_saldo
            novo_saldo = 0.0
            amortizacao = round(amortizacao, 2)
            valor_pago = round(valor_pago, 2)

        # Atualiza estado agregado
        self.total_pago = round(self.total_pago + max(0.0, valor_pago), 2)
        self.saldo_restante = novo_saldo
        
        print(f"💰 Total pago atualizado: {format_brl(self.total_pago)}")
        print(f"💳 Dívida restante atualizada: {format_brl(self.saldo_restante)}")

        # Guarda registro
        registro = {
            "mes": len(self.registros) + 1,
            "data": data_pag.strftime("%d/%m/%Y"),
            "valor": valor_pago,
            "juros": juros,
            "amort": amortizacao,
            "saldo": novo_saldo,
            "status": status,
        }
        
        # Debug: mostrar dados calculados
        print("\n" + "="*60)
        print("🔍 DEBUG - DADOS DO REGISTRO")
        print("="*60)
        print(f"Valor digitado: {valor_digitado}")
        print(f"Valor parseado: {valor_pago}")
        print(f"Data selecionada: {data_pag}")
        print(f"Status: {status}")
        print(f"Modo online: {self.modo_online}")
        print(f"Saldo anterior: R$ {saldo_anterior:,.2f}")
        print(f"Juros (1%): R$ {juros:,.2f}")
        print(f"Amortização: R$ {amortizacao:,.2f}")
        print(f"Novo saldo: R$ {novo_saldo:,.2f}")
        print("="*60)
        
        # Tentar salvar no servidor
        if self.modo_online:
            print("📡 Tentando salvar no servidor...")
            try:
                registro_servidor = {
                    "mes": registro["mes"],
                    "data": registro["data"],
                    "valor": registro["valor"],
                    "juros": registro["juros"],
                    "amort": registro["amort"],
                    "saldo": registro["saldo"],
                    "status": registro["status"],
                    "createdAt": datetime.now().isoformat() + "Z"
                }
                
                print("📤 Dados que serão enviados:")
                import json
                print(json.dumps(registro_servidor, indent=2, ensure_ascii=False))
                
                resultado = persistence.create_registro(registro_servidor)
                registro["server_id"] = resultado.get("id")  # Guardar ID do servidor
                
                print(f"✅ Registro salvo no servidor com ID: {resultado.get('id')}")
                
            except Exception as e:
                print(f"❌ ERRO ao salvar no servidor: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showwarning(
                    "Aviso",
                    f"Erro ao salvar no servidor:\n{e}\n\nRegistro salvo apenas localmente."
                )
        else:
            print("⚠️  Modo offline - registro NÃO será salvo no servidor")
        
        self.registros.append(registro)

        # Atualiza UI
        self._atualiza_resumos()
        self._adiciona_na_tabela(registro)

        # Preparar próximos campos
        self.data_sugerida = next_month(data_pag)
        
        if CALENDARIO_DISPONIVEL:
            self.date_picker.set_date(self.data_sugerida)
        else:
            self.var_data.set(self.data_sugerida.strftime("%d/%m/%Y"))
        
        # Limpar campo de valor
        self.var_valor.set("")
        self.var_status.set("Pago")
        self.entry_valor.focus_set()

        if self.saldo_restante == 0.0:
            messagebox.showinfo("Parabéns", "Dívida quitada! 🎉")

    def _adiciona_na_tabela(self, reg: dict):
        # Determinar tag para cor alternada
        row_count = len(self.tabela.get_children())
        tag = "evenrow" if row_count % 2 == 0 else "oddrow"
        
        self.tabela.insert(
            "",
            "end",
            values=(
                reg["mes"],
                reg["data"],
                format_brl(reg["valor"]),
                format_brl(reg["juros"]),
                format_brl(reg["amort"]),
                format_brl(reg["saldo"]),
                reg["status"],
            ),
            tags=(tag,)
        )

    def _atualiza_resumos(self):
        total_fmt = format_brl(self.total_pago)
        saldo_fmt = format_brl(self.saldo_restante)
        print("\n🔄 Atualizando resumos:")
        print(f"   Total pago: {self.total_pago} → {total_fmt}")
        print(f"   Dívida restante: {self.saldo_restante} → {saldo_fmt}")

        if hasattr(self, "label_total"):
            self.label_total.config(text=total_fmt)

    def alternar_status_selecao(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione uma linha para alternar o status.")
            return
        item_id = sel[0]
        idx = self.tabela.index(item_id)
        if idx < 0 or idx >= len(self.registros):
            return
        atual = self.registros[idx]["status"]
        novo = "Pendente" if atual == "Pago" else "Pago"
        
        # Tentar atualizar no servidor
        if self.modo_online and "server_id" in self.registros[idx]:
            try:
                persistence.update_registro(
                    self.registros[idx]["server_id"],
                    {"status": novo}
                )
            except Exception as e:
                print(f"⚠️  Erro ao atualizar status no servidor: {e}")
                messagebox.showwarning(
                    "Aviso",
                    f"Erro ao atualizar no servidor:\n{e}\n\nStatus alterado apenas localmente."
                )
        
        self.registros[idx]["status"] = novo
        # Atualiza somente a coluna de status na view (reinsere valores)
        vals = list(self.tabela.item(item_id, "values"))
        vals[-1] = novo
        self.tabela.item(item_id, values=vals)

    def desfazer_ultimo(self):
        if not self.registros:
            messagebox.showinfo("Aviso", "Não há registros para desfazer.")
            return

        ultimo = self.registros.pop()
        
        # Tentar deletar do servidor
        if self.modo_online and "server_id" in ultimo:
            try:
                persistence.delete_registro(ultimo["server_id"])
            except Exception as e:
                print(f"⚠️  Erro ao deletar do servidor: {e}")
                messagebox.showwarning(
                    "Aviso",
                    f"Erro ao deletar do servidor:\n{e}\n\nRegistro removido apenas localmente."
                )
        
        # Recalcular agregados a partir do zero para evitar erro acumulado
        self._recalcular_agregado_e_table()

    def reiniciar(self):
        if not messagebox.askyesno("Confirmar", "Reiniciar e apagar todos os registros?"):
            return
        
        # Tentar deletar todos do servidor
        if self.modo_online:
            try:
                persistence.delete_todos_registros()
            except Exception as e:
                print(f"⚠️  Erro ao deletar registros do servidor: {e}")
                messagebox.showwarning(
                    "Aviso",
                    f"Erro ao deletar do servidor:\n{e}\n\nRegistros removidos apenas localmente."
                )
        
        self.registros.clear()
        self.total_pago = 0.0
        self.saldo_restante = self.divida_inicial
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self._atualiza_resumos()
        self.data_sugerida = date.today()
        
        if CALENDARIO_DISPONIVEL:
            self.date_picker.set_date(self.data_sugerida)
        else:
            self.var_data.set(self.data_sugerida.strftime("%d/%m/%Y"))
        
        self.var_valor.set("")
        self.var_status.set("Pago")
        self.entry_valor.focus_set()

    def limpar_historico(self):
        """Remove todos os registros do JSON Server e atualiza a interface."""
        if not self.modo_online:
            messagebox.showwarning(
                "Modo Offline",
                "Não é possível limpar o histórico do servidor.\nO servidor está offline."
            )
            return
        
        # Verificar se servidor ainda está acessível
        if not persistence.verificar_conexao():
            self.modo_online = False
            messagebox.showerror(
                "Servidor Indisponível",
                "O servidor JSON Server não está mais acessível.\n\n"
                "Por favor, inicie o servidor:\n"
                "1. Abra um terminal\n"
                "2. cd servidor\n"
                "3. pnpm start\n\n"
                "Depois, reinicie a aplicação."
            )
            return
        
        if not messagebox.askyesno(
            "Confirmar Limpeza",
            "Isso irá deletar TODOS os registros do JSON Server.\n\nDeseja continuar?"
        ):
            return
        
        try:
            print("\n🗑️  Iniciando limpeza do histórico no servidor...")
            persistence.delete_todos_registros()
            print("✅ Histórico limpo com sucesso no servidor!")
            
            # Limpar dados locais e atualizar interface
            self.registros.clear()
            self.total_pago = 0.0
            self.saldo_restante = self.divida_inicial
            
            # Limpar tabela
            for item in self.tabela.get_children():
                self.tabela.delete(item)
            
            # Atualizar resumos
            self._atualiza_resumos()
            
            # Resetar data sugerida
            self.data_sugerida = date.today()
            if CALENDARIO_DISPONIVEL:
                self.date_picker.set_date(self.data_sugerida)
            else:
                self.var_data.set(self.data_sugerida.strftime("%d/%m/%Y"))
            
            self.var_valor.set("")
            self.var_status.set("Pago")
            self.entry_valor.focus_set()
            
            messagebox.showinfo(
                "Sucesso",
                "Histórico do servidor limpo com sucesso!"
            )
        except Exception as e:
            print(f"❌ Erro ao limpar histórico: {e}")
            import traceback
            traceback.print_exc()
            
            # Verificar se é erro de conexão
            erro_msg = str(e)
            if "não está disponível" in erro_msg or "Servidor" in erro_msg or "fechou a conexão" in erro_msg:
                self.modo_online = False
                messagebox.showerror(
                    "Erro de Conexão",
                    f"{erro_msg}\n\n"
                    "A aplicação foi alterada para modo offline.\n"
                    "Se alguns registros foram deletados, reinicie a aplicação."
                )
            elif "Alguns registros falharam" in erro_msg:
                # Sucesso parcial - alguns foram deletados
                messagebox.showwarning(
                    "Limpeza Parcial",
                    f"{erro_msg}\n\n"
                    "Alguns registros foram deletados com sucesso.\n"
                    "Reinicie a aplicação para sincronizar o estado."
                )
            else:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao limpar histórico do servidor:\n\n{erro_msg}"
                )

    def _recalcular_agregado_e_table(self):
        """Recalcula total_pago e saldo_restante percorrendo registros; re-renderiza tabela."""
        self.total_pago = 0.0
        self.saldo_restante = self.divida_inicial

        # Limpa tabela e re-insere com mês reindexado
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for i, reg in enumerate(self.registros, start=1):
            saldo_anterior = self.saldo_restante
            juros = round(saldo_anterior * self.taxa, 2)
            amort = round(reg["valor"] - juros, 2)
            novo_saldo = round(saldo_anterior - amort, 2)
            if novo_saldo < 0:
                amort += novo_saldo
                reg["valor"] += novo_saldo
                novo_saldo = 0.0
                amort = round(amort, 2)
                reg["valor"] = round(reg["valor"], 2)

            self.total_pago = round(self.total_pago + max(0.0, reg["valor"]), 2)
            self.saldo_restante = novo_saldo

            reg["mes"] = i
            reg["juros"] = juros
            reg["amort"] = amort
            reg["saldo"] = novo_saldo

            self._adiciona_na_tabela(reg)

        self._atualiza_resumos()


def main():
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        else:
            style.theme_use("clam")
    except Exception:
        pass

    app = ControleDividaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
