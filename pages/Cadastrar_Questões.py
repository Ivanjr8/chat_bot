# app.py
import streamlit as st
from db_connection import DatabaseConnection

# Configuração da Página
st.set_page_config(page_title="📚 CRUD Questões", layout="wide")
# Titulo da página
st.title("📚 Gerenciador de Perguntas do Simulado")

# 🔧 Estilo personalizado
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Arquivo de estilo não encontrado.")



# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()

# 🔍 Filtro por módulo
modulos_disponiveis = db.get_modulos()
modulo_opcoes = ["Todos"] + modulos_disponiveis
modulo_selecionado = st.sidebar.selectbox("🔎 Filtrar por módulo", options=modulo_opcoes)

if modulo_selecionado != "Todos":
    perguntas = db.get_perguntas(modulo_selecionado)
else:
    perguntas = db.get_perguntas()

# 📋 Visualização das perguntas
st.subheader("📋 Perguntas cadastradas")

if perguntas and len(perguntas) > 0:
   for row in perguntas:
    codigo = row['CO_PERGUNTA']
    descricao = row['DE_PERGUNTA']

    codigo_formatado = codigo.strip() if codigo else "Sem código"
    descricao_formatada = descricao.strip() if descricao else "Sem descrição"

    with st.expander(f"ID {row['PK_CO_PERGUNTA']} - Código {codigo_formatado}"):
        st.write(descricao_formatada)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✏️ Editar {row['PK_CO_PERGUNTA']}", key=f"editar_{row['PK_CO_PERGUNTA']}"):
                st.session_state["edit_id"] = row['PK_CO_PERGUNTA']
                st.session_state["edit_codigo"] = codigo_formatado
                st.session_state["edit_descricao"] = descricao_formatada
        with col2:
            if st.button(f"❌ Excluir {row['PK_CO_PERGUNTA']}", key=f"excluir_{row['PK_CO_PERGUNTA']}"):
                db.delete_pergunta(row['PK_CO_PERGUNTA'])
                st.success(f"Pergunta {row['PK_CO_PERGUNTA']} excluída.")
                st.rerun()
else:
    st.warning("⚠️ Nenhuma pergunta encontrada para o filtro atual.")

# ➕ Formulário de edição/inserção
st.subheader("➕ Adicionar ou Editar Pergunta")
with st.form("form_crud"):
    id_edicao = st.session_state.get("edit_id", None)
    codigo_input = st.text_input("Pergunta", value=st.session_state.get("edit_codigo", ""))
    descricao_input = st.text_area("Texto", value=st.session_state.get("edit_descricao", ""))
    
    enviar = st.form_submit_button("💾 Salvar")

if enviar:
    if not codigo_input.strip() or not descricao_input.strip():
        st.warning("⚠️ Código e descrição não podem estar vazios.")
    else:
        if id_edicao:
            db.update_pergunta(id_edicao, codigo_input, descricao_input)
            st.success("✅ Pergunta atualizada com sucesso!")
            st.session_state["edit_id"] = None
        else:
            db.insert_pergunta(codigo_input, descricao_input)
            st.success("✅ Pergunta adicionada com sucesso!")
        st.session_state["edit_codigo"] = ""
        st.session_state["edit_descricao"] = ""
        st.rerun()

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

