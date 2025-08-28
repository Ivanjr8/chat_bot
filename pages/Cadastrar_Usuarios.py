import streamlit as st
from db_connection import DatabaseConnection

# 🔧 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.title("🔄 Cadastro ou Atualização de Usuário")
    
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
db = DatabaseConnection()
db.connect()

# 🔍 Selecionar usuário existente ou novo
usuarios = db.get_usuarios()
opcoes = ["➕ Novo usuário"] + [u["usuario"] for u in usuarios]
usuario_selecionado = st.selectbox("Selecione um usuário", opcoes)

# 🔁 Se for usuário existente, preencher dados
if usuario_selecionado != "➕ Novo usuário":
    try:
        usuario_data = next(u for u in usuarios if u.get("usuario") == usuario_selecionado)
        usuario = usuario_data.get("usuario", "")
        perfil_atual = usuario_data.get("perfil", "Aluno")  # Valor padrão seguro
    except StopIteration:
        st.error(f"❌ Usuário '{usuario_selecionado}' não encontrado.")
        st.stop()

    senha = st.text_input("🔒 Nova senha", type="password")
    perfil = st.selectbox(
        "🎓 Perfil",
        ["Aluno", "Professor", "Administrador"],
        index=["Aluno", "Professor", "Administrador"].index(perfil_atual)
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Atualizar"):
            if senha.strip():
                resultado = db.merge_usuario(usuario.strip(), senha.strip(), perfil)
                if resultado == "atualizado":
                    st.success(f"🔁 Usuário '{usuario}' atualizado com sucesso!")
                else:
                    st.error(f"❌ Erro: {resultado}")
            else:
                st.warning("⚠️ Informe uma nova senha para atualizar.")
    with col2:
        if st.button("🗑️ Excluir"):
            resultado = db.delete_usuario(usuario)
            if resultado is True:
                st.success(f"🗑️ Usuário '{usuario}' excluído com sucesso!")
                st.rerun()
            else:
                st.error(f"❌ Erro ao excluir: {resultado}")
# ➕ Adicionar novo usuário
else:
    usuario = st.text_input("👤 Nome de usuário")
    senha = st.text_input("🔒 Senha", type="password")
    perfil = st.selectbox("🎓 Perfil", ["Aluno", "Professor", "Administrador"])
    if st.button("💾 Cadastrar novo"):
        if usuario.strip() and senha.strip():
            resultado = db.merge_usuario(usuario.strip(), senha.strip(), perfil)
            if resultado == "inserido":
                st.success(f"✅ Usuário '{usuario}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.error(f"❌ Erro: {resultado}")
        else:
            st.warning("⚠️ Preencha todos os campos.")

db.close()
