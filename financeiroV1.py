import subprocess
import sys

try:
    import matplotlib.pyplot as plt
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib==3.8.0"])
    import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import matplotlib.pyplot as plt
from calendar import month_name
import pandas as pd
from fpdf import FPDF
import base64
import webbrowser

# Atualizando a função aplicar_estilo_dark
def aplicar_estilo_dark():
    st.markdown(
        """
        <style>
        /* Fundo geral */
        .main {
            background-color: #121212;
            color: #00FFAB; /* Cor neon contrastante */
        }

        /* Fundo da barra lateral */
        .css-1d391kg {
            background-color: #1E1E1E;
        }

        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            color: #00FFAB;
        }

        /* Texto */
        p, label, span, div {
            color: #00FFAB;
        }

        /* Botões da barra lateral */
        .stRadio > div {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .stRadio > div > label {
            background-color: #1E1E1E; /* Fundo padrão (escuro) */
            color: #00FFAB; /* Cor do texto */
            padding: 10px 15px;
            border-radius: 10px; /* Bordas arredondadas */
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent; /* Borda invisível por padrão */
        }
        .stRadio > div > label:hover {
            background-color: #000000; /* Fundo preto no hover */
            color: #00FFAB; /* Texto neon no hover */
            border: 2px solid #00FFAB; /* Borda neon no hover */
        }
        .stRadio > div > label[data-selected="true"] {
            background-color: #000000; /* Fundo preto para o botão selecionado */
            color: #00FFAB; /* Texto neon */
            border: 2px solid #00FFAB; /* Borda neon */
        }

        /* Botões internos */
        .stButton>button {
            background-color: #1E1E1E; /* Fundo escuro */
            color: #00FFAB; /* Texto neon */
            border: 2px solid #00FFAB; /* Borda neon */
            border-radius: 10px; /* Bordas arredondadas */
            padding: 10px 15px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #000000; /* Fundo preto no hover */
            color: #00FFAB; /* Texto neon no hover */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Configurações iniciais
st.set_page_config(
    page_title="Controle Financeiro Pessoal",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Classe de controle financeiro (adaptada do seu código)
class ControleFinanceiro:
    ARQUIVO_DADOS = "dados_financeiros.json"
    
    def __init__(self):
        self.CATEGORIAS = {
            'M': 'Moradia', 
            'T': 'Transporte', 
            'A': 'Alimentação',
            'S': 'Saúde', 
            'L': 'Lazer', 
            'O': 'Outros',
            'C': 'Compras'
        }
        
        self.CATEGORIAS_INVESTIMENTOS = {
            'RF': 'Renda Fixa',
            'RV': 'Renda Variável',
            'FI': 'Fundos Imobiliários',
            'CR': 'Criptomoedas',
            'IN': 'Internacional'
        }
        
        self.saldo = 0
        self.saldo_inicial = 0
        self.saldo_final_mes_anterior = 0
        self.ultimo_mes_verificado = ""
        self.ultima_recarga = ""
        self.pagamentos = []
        self.receitas = []
        self.investimentos = []
        
        if not self.carregar_dados():
            self.inicializar_dados()
        if not hasattr(self, 'investimentos'):
            self.investimentos = []
            
        self.verificar_transacoes_recorrentes()

    def to_dict(self):
        return {
            'saldo': self.saldo,
            'saldo_inicial': self.saldo_inicial,
            'saldo_final_mes_anterior': self.saldo_final_mes_anterior,
            'ultimo_mes_verificado': self.ultimo_mes_verificado,
            'ultima_recarga': self.ultima_recarga,
            'pagamentos': self.pagamentos,
            'receitas': self.receitas,
            'investimentos': self.investimentos,
            'CATEGORIAS': self.CATEGORIAS,
            'CATEGORIAS_INVESTIMENTOS': self.CATEGORIAS_INVESTIMENTOS
        }

    def salvar_dados(self):
        dados = self.to_dict()
        with open(self.ARQUIVO_DADOS, 'w') as f:
            json.dump(dados, f, indent=4)

    def carregar_dados(self):
        if os.path.exists(self.ARQUIVO_DADOS):
            try:
                with open(self.ARQUIVO_DADOS, 'r') as f:
                    dados = json.load(f)
                    self.saldo = dados.get('saldo', 0)
                    self.saldo_inicial = dados.get('saldo_inicial', 0)
                    self.saldo_final_mes_anterior = dados.get('saldo_final_mes_anterior', 0)
                    self.ultimo_mes_verificado = dados.get('ultimo_mes_verificado', '')
                    self.ultima_recarga = dados.get('ultima_recarga', '')
                    self.pagamentos = dados.get('pagamentos', [])
                    self.receitas = dados.get('receitas', [])
                    self.investimentos = dados.get('investimentos', [])
                    self.CATEGORIAS = dados.get('CATEGORIAS', self.CATEGORIAS)
                    self.CATEGORIAS_INVESTIMENTOS = dados.get('CATEGORIAS_INVESTIMENTOS', self.CATEGORIAS_INVESTIMENTOS)
                    return True
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")
                return False
        return False

    def verificar_transacoes_recorrentes(self):
        mes_atual = datetime.now().strftime("%m/%Y")
        recarregou = False
        
        if self.ultimo_mes_verificado == mes_atual:
            return
            
        if self.saldo_final_mes_anterior:
            self.saldo_inicial = self.saldo_final_mes_anterior
        else:
            self.saldo_inicial = self.saldo
        
        if not self.ultima_recarga or self.ultima_recarga != mes_atual:
            self.saldo = self.saldo_inicial
            self.ultima_recarga = mes_atual
            recarregou = True
        
        for despesa in [d for d in self.pagamentos if d.get('recorrente', False)]:
            if not any(d['data'].endswith(mes_atual) and d['descricao'] == despesa['descricao'] for d in self.pagamentos):
                nova_despesa = despesa.copy()
                nova_despesa.update({
                    "data": datetime.now().strftime("01/%m/%Y"),
                    "pago": False,
                    "recorrente": True
                })
                self.pagamentos.append(nova_despesa)
        
        for receita in [r for r in self.receitas if r.get('recorrente', False)]:
            if not any(r['data'].endswith(mes_atual) and r['descricao'] == receita['descricao'] for r in self.receitas):
                nova_receita = receita.copy()
                nova_receita.update({
                    "data": datetime.now().strftime("01/%m/%Y"),
                    "recorrente": True
                })
                self.receitas.append(nova_receita)
                self.saldo += nova_receita['valor']
        
        self.ultimo_mes_verificado = mes_atual
        self.saldo_final_mes_anterior = self.saldo
        self.salvar_dados()
        
        if recarregou:
            st.success(f"Recarga mensal realizada! Saldo recarregado para R$ {self.saldo_inicial:.2f}")

    def inicializar_dados(self):
        self.saldo_inicial = 0
        self.saldo = self.saldo_inicial
        self.saldo_final_mes_anterior = self.saldo_inicial
        self.ultima_recarga = datetime.now().strftime("%m/%Y")
        self.pagamentos = []
        self.receitas = []
        self.investimentos = []
        self.salvar_dados()

    def editar_saldo(self, novo_saldo):
        self.saldo = novo_saldo
        self.salvar_dados()

    def adicionar_transacao(self, tipo, descricao, valor, categoria=None, data=None, parcelas=1, recorrente=False):
        transacao = {
            "descricao": descricao,
            "valor": valor,
            "data": data or datetime.now().strftime("%d/%m/%Y"),
            "pago": False,
            "recorrente": recorrente
        }
        
        if tipo == "despesa":
            transacao["categoria"] = self.CATEGORIAS.get(categoria, categoria)
            
            if parcelas > 1:
                valor_parcela = valor / parcelas
                data_atual = datetime.strptime(data, "%d/%m/%Y") if data else datetime.now()
                
                for i in range(parcelas):
                    data_parcela = (data_atual + timedelta(days=30*i)).strftime("%d/%m/%Y")
                    parcela = transacao.copy()
                    parcela.update({
                        "descricao": f"{descricao} ({i+1}/{parcelas})",
                        "valor": valor_parcela,
                        "data": data_parcela,
                        "parcelado": True,
                        "parcela_atual": i+1,
                        "total_parcelas": parcelas,
                        "valor_total": valor,
                        "recorrente": False
                    })
                    self.pagamentos.append(parcela)
            else:
                self.pagamentos.append(transacao)
        else:
            transacao["recorrente"] = recorrente
            self.receitas.append(transacao)
            self.saldo += valor
            
        self.salvar_dados()

    def adicionar_investimento(self, descricao, valor, categoria, data=None):
        try:
            data_invest = datetime.strptime(data, "%d/%m/%Y") if data else datetime.now()
        except ValueError:
            data_invest = datetime.now()
        
        investimento = {
            "descricao": descricao,
            "valor": valor,
            "categoria": self.CATEGORIAS_INVESTIMENTOS.get(categoria, categoria),
            "data": data_invest.strftime("%d/%m/%Y")
        }
        
        if data_invest >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            if self.saldo < valor:
                raise ValueError("Saldo insuficiente para este investimento")
            self.saldo -= valor
        
        self.investimentos.append(investimento)
        self.salvar_dados()
        return True
    
    def remover_investimento(self, indice):
        if 0 <= indice < len(self.investimentos):
            investimento = self.investimentos[indice]
            self.saldo += investimento['valor']
            del self.investimentos[indice]
            self.salvar_dados()
            return True
        return False

    def remover_transacao(self, indice, tipo):
        if tipo == "despesa":
            if 0 <= indice < len(self.pagamentos):
                transacao = self.pagamentos[indice]
                
                if transacao.get("parcelado", False):
                    desc_base = transacao["descricao"].split(" (")[0]
                    parcelas = [p for p in self.pagamentos if p.get("descricao", "").startswith(desc_base + " (")]
                    
                    for p in reversed(parcelas):
                        idx = self.pagamentos.index(p)
                        if p["pago"]:
                            self.saldo += p["valor"]
                        del self.pagamentos[idx]
                else:
                    if transacao["pago"]:
                        self.saldo += transacao["valor"]
                    del self.pagamentos[indice]
                
                self.salvar_dados()
                return True
        elif tipo == "investimento":
            return self.remover_investimento(indice)
        else:
            if 0 <= indice < len(self.receitas):
                transacao = self.receitas[indice]
                self.saldo -= transacao["valor"]
                del self.receitas[indice]
                self.salvar_dados()
                return True
        return False

    def pagar(self, indice):
        if 0 <= indice < len(self.pagamentos) and not self.pagamentos[indice]["pago"]:
            if self.saldo >= self.pagamentos[indice]["valor"]:
                self.pagamentos[indice]["pago"] = True
                self.saldo -= self.pagamentos[indice]["valor"]
                
                data_pagamento = self.pagamentos[indice]["data"]
                mes_pagamento = data_pagamento[-7:]
                if datetime.now().strftime("%m/%Y") == mes_pagamento:
                    self.saldo_final_mes_anterior = self.saldo
                
                self.salvar_dados()
                return "Pagamento realizado!"
        return "Pagamento não realizado!"

    def calcular_total_investido(self):
        return sum(i['valor'] for i in self.investimentos)

    def calcular_gasto_medio(self, dias=30):
        data_limite = datetime.now() - timedelta(days=dias)
        despesas = [p['valor'] for p in self.pagamentos 
                   if p['pago'] and datetime.strptime(p['data'], "%d/%m/%Y") >= data_limite]
        return sum(despesas) / dias if dias > 0 and despesas else 0

    def dias_ate_saldo_zerar(self):
        gasto_medio = self.calcular_gasto_medio()
        if gasto_medio <= 0:
            return float('inf')
        return self.saldo / gasto_medio

    def gerar_relatorio(self):
        mes_atual = datetime.now().strftime("%m/%Y")
        receitas = sum(r['valor'] for r in self.receitas if r['data'].endswith(mes_atual))
        despesas = sum(p['valor'] for p in self.pagamentos if p['data'].endswith(mes_atual) and p['pago'])
        investimentos = sum(i['valor'] for i in self.investimentos if i['data'].endswith(mes_atual))
        total_investido = self.calcular_total_investido()
        gasto_medio = self.calcular_gasto_medio()
        dias_restantes = self.dias_ate_saldo_zerar()
        
        return (f"Receitas: R$ {receitas:.2f}\n"
                f"Despesas pagas: R$ {despesas:.2f}\n"
                f"Investimentos: R$ {investimentos:.2f}\n"
                f"Total Investido: R$ {total_investido:,.2f}\n"
                f"Saldo: R$ {self.saldo:,.2f}\n"
                f"Gasto médio diário: R$ {gasto_medio:.2f}\n"
                f"Dias até saldo zerar: {dias_restantes:.1f}")

    def gerar_relatorio_pdf(self, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(0, 10, "Relatório Financeiro Completo", ln=1, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Resumo Financeiro", ln=1)
        pdf.set_font("Arial", size=10)
        
        mes_atual = datetime.now().strftime("%m/%Y")
        dados = self.obter_historico_mensal(mes_atual)
        
        pdf.cell(0, 8, f"Saldo Inicial: R$ {dados['saldo_inicial']:,.2f}", ln=1)
        pdf.cell(0, 8, f"Total Receitas: R$ {dados['total_receitas']:,.2f}", ln=1)
        pdf.cell(0, 8, f"Total Despesas: R$ {dados['total_despesas']:,.2f}", ln=1)
        pdf.cell(0, 8, f"Total Investimentos: R$ {dados['total_investimentos']:,.2f}", ln=1)
        pdf.cell(0, 8, f"Saldo Final: R$ {dados['saldo_final']:,.2f}", ln=1)
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Receitas", ln=1)
        pdf.set_font("Arial", size=10)
        
        for r in dados['receitas']:
            pdf.cell(0, 8, f"{r['data']} - {r['descricao']}: R$ {r['valor']:,.2f}", ln=1)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Despesas", ln=1)
        pdf.set_font("Arial", size=10)
        
        for d in dados['despesas']:
            status = "Pago" if d['pago'] else "Pendente"
            pdf.cell(0, 8, f"{d['data']} - {d['descricao']} ({d['categoria']}, {status}): R$ {d['valor']:,.2f}", ln=1)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Investimentos", ln=1)
        pdf.set_font("Arial", size=10)
        
        for inv in dados['investimentos']:
            pdf.cell(0, 8, f"{inv['data']} - {inv['descricao']} ({inv['categoria']}): R$ {inv['valor']:,.2f}", ln=1)
        
        pdf.output(filename)

    def gerar_grafico(self):
        categorias = {cat: 0 for cat in self.CATEGORIAS.values()}
        for p in self.pagamentos:
            if p["pago"] and p["categoria"] in categorias:
                categorias[p["categoria"]] += p["valor"]
        
        categorias = {k: v for k, v in categorias.items() if v > 0}
        
        if not categorias:
            return None
            
        fig, ax = plt.subplots()
        ax.pie(categorias.values(), labels=categorias.keys(), autopct='%1.1f%%')
        return fig

    def gerar_grafico_investimentos(self):
        categorias = {cat: 0 for cat in self.CATEGORIAS_INVESTIMENTOS.values()}
        for i in self.investimentos:
            if i["categoria"] in categorias:
                categorias[i["categoria"]] += i["valor"]
        
        categorias = {k: v for k, v in categorias.items() if v > 0}
        
        if not categorias:
            return None
            
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(categorias.values(), labels=categorias.keys(), autopct='%1.1f%%')
        ax1.set_title('Distribuição de Investimentos')
        
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        bars = ax2.bar(categorias.keys(), categorias.values(), color='purple')
        ax2.set_title('Valor Investido por Categoria')
        ax2.set_ylabel('Valor (R$)')
        
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'R$ {height:,.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        return fig1, fig2

    def obter_historico_mensal(self, mes_ano):
        receitas = [r for r in self.receitas if r['data'][-7:] == mes_ano]
        despesas = [p for p in self.pagamentos if p['data'][-7:] == mes_ano]
        investimentos = [i for i in self.investimentos if i['data'][-7:] == mes_ano]
        
        saldo_inicial = self.saldo_inicial if mes_ano == self.ultima_recarga else 0
        
        total_receitas = sum(r['valor'] for r in receitas)
        total_despesas = sum(p['valor'] for p in despesas if p['pago'])
        total_investimentos = sum(i['valor'] for i in investimentos)
        saldo_final = saldo_inicial + total_receitas - total_despesas - total_investimentos
        
        return {
            'receitas': receitas,
            'despesas': despesas,
            'investimentos': investimentos,
            'saldo_inicial': saldo_inicial,
            'saldo_final': saldo_final,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'total_investimentos': total_investimentos
        }

    def obter_todos_meses_com_dados(self):
        meses = set()
        for transacao in self.receitas + self.pagamentos + self.investimentos:
            data = transacao['data']
            mes_ano = data[-7:]
            meses.add(mes_ano)
        return sorted(meses, key=lambda x: (int(x[3:]), int(x[:2])))

    def filtrar_transacoes(self, tipo=None, categoria=None, data_inicio=None, data_fim=None, valor_min=None, valor_max=None, pago=None):
        transacoes = []
        
        if tipo == "receita" or tipo is None:
            transacoes.extend(self.receitas)
        if tipo == "despesa" or tipo is None:
            transacoes.extend(self.pagamentos)
        if tipo == "investimento" or tipo is None:
            transacoes.extend(self.investimentos)
        
        filtradas = []
        for t in transacoes:
            if tipo is not None:
                if tipo == "despesa" and 'categoria' not in t:
                    continue
                if tipo == "receita" and 'categoria' in t:
                    continue
                if tipo == "investimento" and t not in self.investimentos:
                    continue
            
            if categoria is not None:
                if 'categoria' in t and t['categoria'] != categoria:
                    continue
                if 'categoria' not in t and tipo == "despesa":
                    continue
            
            if data_inicio is not None or data_fim is not None:
                try:
                    data_trans = datetime.strptime(t['data'], "%d/%m/%Y")
                    if data_inicio is not None and data_trans < data_inicio:
                        continue
                    if data_fim is not None and data_trans > data_fim:
                        continue
                except ValueError:
                    continue
            
            if valor_min is not None and t['valor'] < valor_min:
                continue
            if valor_max is not None and t['valor'] > valor_max:
                continue
            
            if pago is not None and 'pago' in t and t['pago'] != pago:
                continue
            
            filtradas.append(t)
        
        return filtradas

# Funções auxiliares para a interface
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def create_download_link(val, filename):
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download {filename}</a>'

# Interface Streamlit
def main():
    aplicar_estilo_dark()  # Aplica o tema dark
    st.title("💰 Controle Financeiro Pessoal")
    
    # Botão "Início" no Header
    if st.button("Início", key="button_inicio"):
        st.session_state.operacao = "Dashboard"  # Define a operação como "Dashboard"

    # Inicializar controle financeiro
    if 'controle' not in st.session_state:
        st.session_state.controle = ControleFinanceiro()
    if 'operacao' not in st.session_state:
        st.session_state.operacao = "Dashboard"  # Define a operação inicial como "Dashboard"
    
    controle = st.session_state.controle
    operacao = st.session_state.operacao

    # Sidebar com menu de navegação
    with st.sidebar:
        st.image("https://i.imgur.com/DeQaC89.png", width=300)
        
        # Menu de navegação com opções em formato de rádio
        menu_opcoes = [
            "Dashboard",
            "Adicionar Receita",
            "Adicionar Despesa",
            "Adicionar Investimento",
            "Registrar Pagamento",
            "Editar Saldo",
            "Relatórios",
            "Histórico",
            "Filtrar Transações"
        ]
        st.session_state.operacao = st.radio("Escolha uma operação:", menu_opcoes, index=menu_opcoes.index(operacao))
    
    # Dashboard
    if st.session_state.operacao == "Dashboard":
        st.markdown("### 🌟 **Visão Geral do Controle Financeiro**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💵 Saldo Atual", formatar_moeda(controle.saldo))
            st.metric("📈 Total Investido", formatar_moeda(controle.calcular_total_investido()))
        
        with col2:
            st.metric("📉 Gasto Médio Diário", formatar_moeda(controle.calcular_gasto_medio()))
            dias_restantes = controle.dias_ate_saldo_zerar()
            st.metric("⏳ Dias até Saldo Zerar", f"{dias_restantes:.1f}" if dias_restantes != float('inf') else "∞")
        
        with col3:
            st.metric("✔️ Despesas Pagas", formatar_moeda(sum(p['valor'] for p in controle.pagamentos if p['pago'])))
            st.metric("❌ Despesas a Pagar", formatar_moeda(sum(p['valor'] for p in controle.pagamentos if not p['pago'])))
        
        st.markdown("---")
        st.markdown("### 📊 **Gráficos e Listagens**")
        tab1, tab2 = st.tabs(["Despesas", "Investimentos"])
        
        # Aba de Despesas
        with tab1:
            st.write("#### Gráfico de Despesas")
            fig_despesas = controle.gerar_grafico()
            if fig_despesas:
                st.pyplot(fig_despesas)
            else:
                st.warning("Não há dados suficientes para gerar o gráfico de despesas.")
            
            st.write("#### Lista de Despesas")
            despesas_df = pd.DataFrame(controle.pagamentos)
            if not despesas_df.empty:
                despesas_df['Valor'] = despesas_df['valor'].apply(lambda x: formatar_moeda(x))
                despesas_df['Data de Vencimento'] = despesas_df['data']
                despesas_df['Status'] = despesas_df['pago'].apply(lambda x: "Pago" if x else "Em Aberto")
                st.dataframe(
                    despesas_df[['descricao', 'Valor', 'Data de Vencimento', 'categoria', 'Status']],
                    column_config={
                        "descricao": "Descrição",
                        "Valor": "Valor",
                        "Data de Vencimento": "Data de Vencimento",
                        "categoria": "Categoria",
                        "Status": "Status"
                    },
                    hide_index=True
                )
            else:
                st.info("Nenhuma despesa cadastrada.")
        
        # Aba de Investimentos
        with tab2:
            st.write("#### Gráficos de Investimentos")
            graficos = controle.gerar_grafico_investimentos()
            if graficos:
                fig1, fig2 = graficos
                st.pyplot(fig1)
                st.pyplot(fig2)
            else:
                st.warning("Não há investimentos registrados para gerar os gráficos.")
            
            st.write("#### Lista de Investimentos")
            investimentos_df = pd.DataFrame(controle.investimentos)
            if not investimentos_df.empty:
                investimentos_df['Valor'] = investimentos_df['valor'].apply(lambda x: formatar_moeda(x))
                investimentos_df['Data'] = investimentos_df['data']
                st.dataframe(
                    investimentos_df[['descricao', 'Valor', 'Data', 'categoria']],
                    column_config={
                        "descricao": "Descrição",
                        "Valor": "Valor",
                        "Data": "Data",
                        "categoria": "Categoria"
                    },
                    hide_index=True
                )
            else:
                st.info("Nenhum investimento cadastrado.")
    
    # Registrar Pagamento
    elif operacao == "Registrar Pagamento":
        st.subheader("Registrar Pagamento de Despesa")
        
        # Filtrar despesas pendentes
        despesas_pendentes = [p for p in controle.pagamentos if not p['pago']]
        
        if not despesas_pendentes:
            st.info("Não há despesas pendentes para pagamento.")
        else:
            # Exibir tabela de despesas pendentes
            despesas_df = pd.DataFrame(despesas_pendentes)
            despesas_df['Valor'] = despesas_df['valor'].apply(lambda x: formatar_moeda(x))
            
            st.write("Despesas Pendentes:")
            st.dataframe(
                despesas_df[['data', 'descricao', 'Valor', 'categoria']],
                column_config={
                    "data": "Data",
                    "descricao": "Descrição",
                    "categoria": "Categoria"
                },
                hide_index=True
            )
            
            # Selectbox com key única
            descricao_despesa = st.selectbox(
                "Selecione a despesa para pagar:",
                [d['descricao'] for d in despesas_pendentes],
                key="selectbox_despesa_pagamento"
            )
            
            # Botão com key única
            if st.button("Registrar Pagamento", key="button_registrar_pagamento"):
                # Encontrar o índice da despesa selecionada
                indice = next((i for i, p in enumerate(controle.pagamentos) 
                            if p['descricao'] == descricao_despesa), None)
                if indice is not None:
                    # Realizar o pagamento
                    resultado = controle.pagar(indice)
                    st.success(resultado)
                    
                    # Atualizar o estado manualmente
                    st.session_state.controle = controle
            
    # Editar Saldo
    elif operacao == "Editar Saldo":
        st.subheader("Editar Saldo Atual")
        
        novo_saldo = st.number_input(
            "Novo valor do saldo (R$)",
            value=float(controle.saldo),
            step=0.01
        )
        
        if st.button("Atualizar Saldo"):
            controle.editar_saldo(novo_saldo)
            st.success("Saldo atualizado com sucesso!")
            st.session_state.controle = controle
        
        # Relatórios
    elif operacao == "Relatórios":
            st.subheader("Relatórios Financeiros")
        
            tab1, tab2 = st.tabs(["Relatório Mensal", "Exportar para PDF"])
            
            with tab1:
                st.text_area(
                    "Resumo Financeiro",
                    controle.gerar_relatorio(),
                    height=200
                )
                
                # Gráficos no relatório
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Distribuição de Despesas")
                    fig_despesas = controle.gerar_grafico()
                    if fig_despesas:
                        st.pyplot(fig_despesas)
                
                with col2:
                    st.write("Distribuição de Investimentos")
                    graficos = controle.gerar_grafico_investimentos()
                    if graficos:
                        st.pyplot(graficos[0])
            
            with tab2:
                st.write("Exportar relatório completo para PDF")
                
                if st.button("Gerar PDF"):
                    filename = "relatorio_financeiro.pdf"
                    controle.gerar_relatorio_pdf(filename)
                    
                    with open(filename, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    
                    st.markdown(
                        f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{filename}">Download Relatório PDF</a>',
                        unsafe_allow_html=True
                    )
    
    # Histórico
    elif operacao == "Histórico":
        st.subheader("Histórico Financeiro")
        
        meses_disponiveis = controle.obter_todos_meses_com_dados()
        if not meses_disponiveis:
            st.warning("Não há dados históricos disponíveis.")
            return
        
        mes_selecionado = st.selectbox(
            "Selecione o mês para visualizar:",
            meses_disponiveis,
            index=len(meses_disponiveis)-1
        )
        
        dados_mes = controle.obter_historico_mensal(mes_selecionado)
        mes, ano = mes_selecionado.split('/')
        nome_mes = month_name[int(mes)]
        
        st.subheader(f"{nome_mes} de {ano}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Saldo Inicial", formatar_moeda(dados_mes['saldo_inicial']))
        col2.metric("Total Receitas", formatar_moeda(dados_mes['total_receitas']))
        col3.metric("Total Despesas", formatar_moeda(dados_mes['total_despesas']))
        col4.metric("Saldo Final", formatar_moeda(dados_mes['saldo_final']))
        
        tab1, tab2, tab3 = st.tabs(["Receitas", "Despesas", "Investimentos"])
        
        with tab1:
            if not dados_mes['receitas']:
                st.info("Nenhuma receita registrada neste mês.")
            else:
                receitas_df = pd.DataFrame(dados_mes['receitas'])
                receitas_df['Valor'] = receitas_df['valor'].apply(lambda x: formatar_moeda(x))
                st.dataframe(
                    receitas_df[['data', 'descricao', 'Valor']],
                    column_config={
                        "data": "Data",
                        "descricao": "Descrição"
                    },
                    hide_index=True
                )
        
        with tab2:
            if not dados_mes['despesas']:
                st.info("Nenhuma despesa registrada neste mês.")
            else:
                despesas_df = pd.DataFrame(dados_mes['despesas'])
                despesas_df['Valor'] = despesas_df['valor'].apply(lambda x: formatar_moeda(x))
                despesas_df['Status'] = despesas_df['pago'].apply(lambda x: "Pago" if x else "Pendente")
                st.dataframe(
                    despesas_df[['data', 'descricao', 'Valor', 'categoria', 'Status']],
                    column_config={
                        "data": "Data",
                        "descricao": "Descrição",
                        "categoria": "Categoria"
                    },
                    hide_index=True
                )
        
        with tab3:
            if not dados_mes['investimentos']:
                st.info("Nenhum investimento registrado neste mês.")
            else:
                investimentos_df = pd.DataFrame(dados_mes['investimentos'])
                investimentos_df['Valor'] = investimentos_df['valor'].apply(lambda x: formatar_moeda(x))
                st.dataframe(
                    investimentos_df[['data', 'descricao', 'Valor', 'categoria']],
                    column_config={
                        "data": "Data",
                        "descricao": "Descrição",
                        "categoria": "Categoria"
                    },
                    hide_index=True
                )
    
    # Filtrar Transações
    elif operacao == "Filtrar Transações":
        st.subheader("Filtrar Transações")
        
        with st.form("form_filtrar"):
            col1, col2 = st.columns(2)
            
            with col1:
                tipo = st.selectbox(
                    "Tipo de Transação",
                    ["Todos", "Receita", "Despesa", "Investimento"]
                )
                
                data_inicio = st.date_input("Data Inicial")
                valor_min = st.number_input("Valor Mínimo (R$)", min_value=0.0, value=0.0)
            
            with col2:
                if tipo == "Despesa":
                    categoria = st.selectbox(
                        "Categoria",
                        ["Todas"] + list(controle.CATEGORIAS.values())
                    )
                    status = st.selectbox(
                        "Status",
                        ["Todos", "Pago", "Pendente"]
                    )
                else:
                    categoria = None
                    status = None
                
                data_fim = st.date_input("Data Final")
                valor_max = st.number_input("Valor Máximo (R$)", min_value=0.0, value=100000.0)
            
            if st.form_submit_button("Aplicar Filtros"):
                # Converter filtros para o formato esperado
                tipo_filtro = None if tipo == "Todos" else tipo.lower()
                categoria_filtro = None if categoria in [None, "Todas"] else categoria
                pago_filtro = None
                if status == "Pago":
                    pago_filtro = True
                elif status == "Pendente":
                    pago_filtro = False
                
                # Aplicar filtros
                transacoes_filtradas = controle.filtrar_transacoes(
                    tipo=tipo_filtro,
                    categoria=categoria_filtro,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    valor_min=valor_min,
                    valor_max=valor_max,
                    pago=pago_filtro
                )
                
                # Mostrar resultados
                if not transacoes_filtradas:
                    st.warning("Nenhuma transação encontrada com os filtros aplicados.")
                else:
                    st.success(f"{len(transacoes_filtradas)} transações encontradas.")
                    
                    # Converter para DataFrame para exibição
                    df = pd.DataFrame(transacoes_filtradas)
                    
                    # Adicionar coluna de tipo
                    df['Tipo'] = df.apply(
                        lambda x: 'Despesa' if 'categoria' in x and x['categoria'] in controle.CATEGORIAS.values() 
                        else 'Investimento' if 'categoria' in x 
                        else 'Receita', 
                        axis=1
                    )
                    
                    # Formatar valor
                    df['Valor'] = df.apply(
                        lambda x: f"-{formatar_moeda(x['valor'])}" if x['Tipo'] == 'Despesa' 
                        else formatar_moeda(x['valor']), 
                        axis=1
                    )
                    
                    # Selecionar colunas para exibição
                    colunas = ['data', 'descricao', 'Valor', 'Tipo']
                    if 'categoria' in df.columns:
                        colunas.insert(3, 'categoria')
                    if 'pago' in df.columns:
                        df['Status'] = df['pago'].apply(lambda x: 'Pago' if x else 'Pendente')
                        colunas.append('Status')
                    
                    st.dataframe(
                        df[colunas],
                        column_config={
                            "data": "Data",
                            "descricao": "Descrição",
                            "categoria": "Categoria"
                        },
                        hide_index=True
                    )

if __name__ == "__main__":
    main()
