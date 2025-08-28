import streamlit as st
from db_connection import DatabaseConnection

# Configuração da Página
st.set_page_config(page_title="📚 CRUD Escolas", layout="wide")
# Titulo da página
st.title("🏫 Cadastro de Escolas")

# 🔧 Estilo personalizado
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Arquivo de estilo não encontrado.")


# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()


# 🔍 Filtro por nome
filtro_nome = st.text_input("Filtrar por nome da escola")

# 📋 Listar escolas
escolas = db.get_escolas(filtro_nome)

if not escolas:
    st.warning("Nenhuma escola encontrada.")
else:
    for escola in escolas:
        with st.expander(f"📘 {escola['NO_ESCOLA']}"):
            novo_nome = st.text_input("Editar nome", value=escola['NO_ESCOLA'], key=f"edit_{escola['PK_ID_ESCOLA']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Atualizar", key=f"update_{escola['PK_ID_ESCOLA']}"):
                    sucesso = db.update_escola(escola['PK_ID_ESCOLA'], novo_nome)
                    if sucesso:
                        st.success("Escola atualizada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar.")
                        
            with col2:
                if st.button("🗑️ Excluir", key=f"delete_{escola['PK_ID_ESCOLA']}"):
                    sucesso = db.delete_escola(escola['PK_ID_ESCOLA'])
                    if sucesso:
                        st.success("Escola excluída.")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir.")
                      
                        

st.markdown("---")

# ➕ Adicionar nova escola
st.subheader("Adicionar nova escola")
novo_nome_escola = st.text_input("Nome da nova escola")

if st.button("➕ Cadastrar"):
    if novo_nome_escola.strip():
        db.insert_escola(novo_nome_escola.strip())
        st.success("Escola cadastrada com sucesso!")
        st.rerun()
    else:
        st.error("O nome da escola não pode estar vazio.")
       
        
# 🔒 Encerrando conexão
db.close()

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