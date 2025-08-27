import streamlit as st
import pyodbc
import pandas as pd

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Estilização da barra lateral
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
           background: linear-gradient( #000000, #0000004c, #06080075);
           color: white;
           box-shadow: 0 0 10px rgba(0,0,0,0.5);
           padding: 20px;
           border-radius: 10px;
        }
       
        [data-testid="stSidebar"] {
           height: 100vh;
        overflow-y: auto;
}

        [data-testid="stSidebar"] h2 {
            color: #10b981;
        }
        [data-testid="stSidebar"] .stButton button {
           background-color: #0000004c;
           color: rgba(245, 245, 245, 0.849);
           text-align: left;
           padding-left: 12px;
           width: 240px;
           height: 40px;
           border: none;
           border-radius: 8px;
           font-size: 18px;
           font-weight: bold;
           box-shadow: 0 4px 6px rgba(0,0,0,0.1);
           cursor: pointer;
           transition: background-color 0.3s ease-in-out;
           display: flex;
           justify-content: flex-start;   /* Alinha conteúdo à esquerda */
           align-items: center;           /* Centraliza verticalmente */
           padding-left: 12px;            /* Espaço interno à esquerda */
           text-align: left;              /* Redundante, mas seguro */
        }
    </style>
""", unsafe_allow_html=True)

# 🧭 Barra lateral personalizada
with st.sidebar:
    st.markdown("## 🧭 Navegação")
    if st.button("🎓   Chatbot", key="btn_chatbot"):
       st.switch_page("pages/chatbot.py")
    if st.button("🖥️   Gerar Simulado", key="btn_simulado"):
        st.switch_page("pages/Gerar_Simulado.py")
    if st.button("✅   Teste de Conexão", key="btn_azure"):
        st.switch_page("pages/conn_azure.py")
    if st.button("↩️   Retornar", key="btn_retornar"):
        st.switch_page("gemini.py")
    st.markdown("---")
    st.markdown("## ⚙️   Cadastro")
    if st.button("🗂️   Questões", key="btn_cadastrar"):
        st.switch_page("pages/Cadastrar_Questões.py")
    if st.button("🗂️   Respostas", key="btn_cadastrar_respostas"):
        st.switch_page("pages/Cadastrar_Respostas.py")
        st.markdown("---")
    
    st.markdown("---")
    st.markdown("### 📞   Suporte")
    st.write("Email: suporte@meuapp.com")

# 🎯 Configuração da página
st.set_page_config(page_title="📘 SimuladoPerguntas", layout="wide", page_icon="📘")

# 💅 Estilo customizado
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .block-container { padding-top: 2rem; }
    .stDataFrame th, .stDataFrame td {
        font-size: 15px;
        padding: 8px;
    }
    .stDataFrame tbody tr:hover {
        background-color: #e6f7ff;
    }
    </style>
""", unsafe_allow_html=True)

# 🔌 Conexão com o banco
def conectar_banco():
    try:
        conexao = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=myfreesqldbserver-0101.database.windows.net;"
            "DATABASE=myFreeDB;"
            "UID=ivan;"
            "PWD=MigMat01#!;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return conexao
    except Exception as erro:
        st.error(f"❌ Erro ao conectar: {erro}")
        return None

# 📥 Carregar dados
def carregar_dados():
    conexao = conectar_banco()
    if conexao:
        try:
            consulta = "SELECT * FROM [dbo].[SimuladoPerguntas]"
            df = pd.read_sql(consulta, conexao)
            return df
        except Exception as erro:
            st.error(f"❌ Erro ao carregar dados: {erro}")
            return None
        finally:
            conexao.close()

# 🧠 Interface
st.title("📘 Tabela de Perguntas Simuladas")
st.subheader("Visualização interativa e filtrável")

dados = carregar_dados()

if dados is not None and not dados.empty:
    # 🔍 Filtros
    with st.expander("🔎 Filtros avançados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            filtro_modulo = st.selectbox("Filtrar por módulo", options=["Todos"] + sorted(dados["FK_MODULO"].unique().tolist()))
        with col2:
            filtro_texto = st.text_input("Buscar por palavra-chave na pergunta")

        if filtro_modulo != "Todos":
            dados = dados[dados["FK_MODULO"] == filtro_modulo]
        if filtro_texto:
            dados = dados[dados["pergunta"].str.contains(filtro_texto, case=False, na=False)]

    # 🧾 Exibição estilizada
    st.markdown("### 📄 Resultados da consulta")
    st.dataframe(
        dados.style.set_properties(**{
            'background-color': '#ffffff',
            'color': '#333333',
            'border-color': '#cccccc'
        }).highlight_null(color='lightgray'),
        use_container_width=True,
        height=600
    )
else:
    st.warning("⚠️ Nenhum dado encontrado ou erro na consulta.")