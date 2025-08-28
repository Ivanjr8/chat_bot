# app.py
import streamlit as st
from streamlit_modal import Modal
from db_connection import DatabaseConnection

# Configuração da Página
st.set_page_config(page_title="Simulado SAEB", page_icon="🧠", layout="wide")
# Titulo da página
# st.title("📚 Gerenciador de Perguntas do Simulado") # adicionar título e smile

# 🔧  Estilo personalizado
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Arquivo de estilo não encontrado.")

# Conexão com o banco
db = DatabaseConnection()
db.connect()

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()

# Função para listar usuários
def listar_usuarios():
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT usuario FROM TB_010_USUARIOS ORDER BY usuario")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Erro ao buscar usuários: {e}")
        return []

# Login com Modal
modal = Modal("🔐 Portal de Acesso", key="login_modal", max_width=600)

#st.set_page_config(page_title="📚 CRUD Simulado", layout="wide")
st.title("📚 Gerenciador de Perguntas do Simulado")

st.markdown("---")
st.markdown("""
            Este é um aplicativo que utiliza IA com consultas ao chatbot (GEMINI) para gerar simulados de acordo com descritores,
            apresentando sugestões de conteúdo para estudo das questões respondidas de forma errada.

            - 📚 [Documentação oficial do Streamlit](https://docs.streamlit.io/)
            - 🐞 [Reportar falhas ou bugs](https://github.com/streamlit/streamlit/issues)
        """)

st.markdown("### 🧪 Bem-vindo ao APP Simulado assistido por IA")
st.markdown("---")

  
if "usuario" not in st.session_state:
    if st.button("Fazer Login"):
        modal.open()

    if modal.is_open():
        with modal.container():
            usuarios = listar_usuarios()
            usuario = st.selectbox("Usuário", usuarios, key="usuario_modal")
            senha = st.text_input("Senha", type="password", key="senha_modal")

            if st.button("Entrar", key="btn_login_modal"):
                perfil = db.autenticar_usuario(usuario, senha)
                if perfil:
                    st.session_state.perfil = perfil
                    st.session_state.usuario = usuario
                    st.success(f"✅ Bem-vindo, {usuario}!")
                    modal.close()
                else:
                    st.error("❌ Usuário ou senha inválidos.")

# Conteúdo após login
# 🔧 Estilo personalizado
if "usuario" in st.session_state:

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
        if st.button("🗂️   Matriz de Acesso", key="btn_matriz"):
            st.switch_page("pages/acesso.py")
        
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

        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

            