import streamlit as st
import pyodbc
import pandas as pd

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuração da Página
st.set_page_config(page_title="Listar Perguntas", layout="wide")
# Titulo da página
st.title("🚧 Listar Perguntas - Página em Construção")
# Adicionar Imagem 
st.image("em_construcao.jpg", caption="Estamos trabalhando nisso!", width=300)

# 🧭 Barra lateral personalizada
with st.sidebar:
        if "usuario" in st.session_state and "perfil" in st.session_state:
            st.markdown(f"""
            👋 Olá, **{st.session_state.usuario}**  
            🔐 Perfil: **{st.session_state.perfil}**
            """)
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
        if st.button("🗂️   Cadastrar Usuários", key="btn_cadastrar_usuarios"):
            st.switch_page("pages/Cadastrar_Usuarios.py")
            st.markdown("---")
        
        st.markdown("---")
        st.markdown("### 📞   Suporte")
        st.write("Email: suporte@meuapp.com")
        
        # Botão para sair
        if st.button("🚪 Sair"):
        # Remove dados de sessão
            for key in ["usuario", "perfil", "usuario_id"]:
                st.session_state.pop(key, None)
        # Redireciona para a página inicial (gemini.py)
                st.switch_page("gemini.py")
            # Reinicia a aplicação
                st.rerun()

# 🔌 Conexão com o banco
def conectar_banco():
    try:
        conexao = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=srvappmba.database.windows.net;"
            "DATABASE=MBA-APP;"
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