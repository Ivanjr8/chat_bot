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
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil

    # 🔍 Função para buscar acessos permitidos
def buscar_acessos_permitidos(perfil):
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT id_modulo FROM TB_012_ACESSOS WHERE perfil = ?", (perfil,))
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Erro ao buscar acessos: {e}")
        return []

# 🗺️ Mapeamento de módulos para botões e páginas
botoes_paginas = {
    1: {"label": "🎓   Chatbot", "page": "pages/chatbot.py", "key": "btn_chatbot"},
    2: {"label": "🖥️   Gerar Simulado", "page": "pages/Gerar_Simulado.py", "key": "btn_simulado"},
    3: {"label": "✅   Teste de Conexão", "page": "pages/conn_azure.py", "key": "btn_azure"},
}  
botoes_cadastro = {
    4: {"label": "🗂️   Questões", "page": "pages/Cadastrar_Questões.py", "key": "btn_cadastrar"},
    5: {"label": "🗂️   Respostas", "page": "pages/Cadastrar_Respostas.py", "key": "btn_cadastrar_respostas"},
    6: {"label": "🗂️   Cadastrar Usuários", "page": "pages/Cadastrar_Usuarios.py", "key": "btn_cadastrar_usuarios"},
    7: {"label": "🗂️   Cadastrar_Escolas", "page": "pages/Cadastrar_Escolas.py", "key": "btn_escolas"},
    8: {"label": "🗂️   matriz", "page": "pages/matriz.py", "key": "btn_matriz"},#
    99: {"label": "↩️   Retornar", "page": "gemini.py", "key": "btn_retornar"},  # acesso universal
}   
#botoes_admin = { 
#   8: {"label": "🗂️   matriz", "page": "pages/matriz.py", "key": "btn_matriz"},
    
#}

# 🔧 Conteúdo após login
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil
    usuario = st.session_state.usuario

    modulos_permitidos = buscar_acessos_permitidos(perfil)

    with st.sidebar:
        st.markdown(f"""
        👋 Olá, **{usuario}**  
        🔐 Perfil: **{perfil}**
        """)
        st.markdown("## 🧭 Navegação")

        for mod_id in modulos_permitidos:
            if mod_id in botoes_paginas:
                btn = botoes_paginas[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_navegacao"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])
        st.markdown("---")
        st.markdown("## ⚙️   Cadastro")
        
        for mod_id in modulos_permitidos + [99]:
            if mod_id in botoes_cadastro:
                btn = botoes_cadastro[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                if st.button(btn["label"], key=chave_unica):
                 st.switch_page(btn["page"])
       
        st.markdown("---")
        st.markdown("## ⚙️   Administrativo")
        
        for mod_id in modulos_permitidos:
            if mod_id in botoes_admin:
                btn = botoes_admin[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_adm"
                if st.button(btn["label"], key=chave_unica):
                  st.switch_page(btn["page"])
        
        st.markdown("---")
        st.markdown("### 📞   Suporte")
        st.write("Email: suporte@meuapp.com")

        # 🚪 Botão para sair
        if st.button("🚪 Sair"):
            for key in ["usuario", "perfil", "usuario_id"]:
                st.session_state.pop(key, None)
            st.switch_page("gemini.py")
            st.rerun()

        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

            