import streamlit as st
from db_connection import DatabaseConnection

# Estilo
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuração
st.set_page_config(page_title="Simulado SAEB", page_icon="🧠", layout="wide")

# Conexão
db = DatabaseConnection()
db.connect()

if not db.conn:
    st.error("❌ Conexão com o banco falhou.")
    st.stop()

# Login
st.title("🔐 Portal de Autenticação")
usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")
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


if st.button("Entrar"):
    perfil = db.autenticar_usuario(usuario, senha)
    if perfil:
        st.success(f"Bem-vindo, {usuario} ({perfil})")
        st.session_state.perfil = perfil
        st.session_state.usuario = usuario
    else:
        st.error("Usuário ou senha inválidos")
    
    
# Verifica se o usuário está logado
    if "perfil" in st.session_state:
        st.sidebar.markdown("---")
    if st.sidebar.button("🚪  Logout"):
        # Limpa a sessão
        st.session_state.clear()
        st.success("Logout realizado com sucesso!")
        st.rerun()  # Recarrega a página

# Menu lateral
if "perfil" in st.session_state:
    perfil = st.session_state.perfil
    st.sidebar.markdown("## 🧭 Navegação")

    if st.sidebar.button("🎓   Chatbot"):
        st.switch_page("pages/chatbot.py")
    if st.sidebar.button("🖥️   Gerar Simulado"):
        st.switch_page("pages/Gerar_Simulado.py")
    if perfil == "Administrador" and st.sidebar.button("✅   Teste de Conexão"):
        st.switch_page("pages/conn_azure.py")
    if st.sidebar.button("↩️   Retornar"):
        st.switch_page("gemini.py")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⚙️   Cadastro")

    if perfil in ["Professor", "Administrador"]:
        if st.sidebar.button("🗂️   Questões"):
            st.switch_page("pages/Cadastrar_Questões.py")
        if st.sidebar.button("🗂️   Respostas"):
            st.switch_page("pages/Cadastrar_Respostas.py")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📞   Suporte")
    st.sidebar.write("Email: suporte@meuapp.com")

    st.markdown(f"### 👋 Olá, {st.session_state.usuario}! Você está logado como **{perfil}**.")

# Conteúdo principal
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🎒 Aplicação para Avaliação de Alunos</h1>", unsafe_allow_html=True)

with st.expander("ℹ️ Sobre este portal"):
    st.markdown("""
        Este é um aplicativo que utiliza IA com consultas ao chatbot (GEMINI) para gerar simulados de acordo com descritores,
        apresentando sugestões de conteúdo para estudo das questões respondidas de forma errada.

        - 📚 [Documentação oficial do Streamlit](https://docs.streamlit.io/)
        - 🐞 [Reportar falhas ou bugs](https://github.com/streamlit/streamlit/issues)
    """)

st.divider()
st.markdown("### 🧪 Bem-vindo ao APP Simulado assistido por IA")