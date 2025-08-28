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
modulos_disponiveis = db.get_modulos() or []
modulo_opcoes = ["Todos"] + modulos_disponiveis
modulo_selecionado = st.sidebar.selectbox("🔎 Filtrar por módulo", options=modulo_opcoes)

# 🔎 Recupera perguntas com base no filtro
if modulo_selecionado != "Todos":
    perguntas = db.get_perguntas(modulo_selecionado) or []
else:
    perguntas = db.get_perguntas() or []

# ⚠️ Tratamento para lista vazia
if not perguntas:
    st.warning("Nenhuma pergunta encontrada para o módulo selecionado.")
else:
    # Aqui você pode exibir as perguntas como quiser
    for pergunta in perguntas:
        st.write(f"• {pergunta}")

# 📋 Visualização das perguntas
st.subheader("📋 Perguntas cadastradas")

# 📋 Visualização das perguntas
st.subheader("📋 Perguntas cadastradas")

if perguntas:
    for row in perguntas:
        # Acessa os campos com segurança
        id_pergunta = row.get('PK_CO_PERGUNTA', 'ID desconhecido')
        codigo = row.get('CO_PERGUNTA', '').strip() or 'Sem código'
        descricao = row.get('DE_PERGUNTA', '').strip() or 'Sem descrição'

        with st.expander(f"ID {id_pergunta} - Código {codigo}"):
            st.write(descricao)

            col1, col2 = st.columns(2)

            with col1:
                editar_key = f"editar_{id_pergunta}"
                if st.button(f"✏️ Editar", key=editar_key):
                    if "edit_id" not in st.session_state:
                        st.session_state["edit_id"] = id_pergunta
                    if "edit_codigo" not in st.session_state:
                        st.session_state["edit_codigo"] = codigo
                    if "edit_descricao" not in st.session_state:
                        st.session_state["edit_descricao"] = descricao

            with col2:
                excluir_key = f"excluir_{id_pergunta}"
                if st.button(f"❌ Excluir", key=excluir_key):
                    try:
                        db.delete_pergunta(id_pergunta)
                        st.success(f"Pergunta {id_pergunta} excluída com sucesso.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir pergunta: {e}")
else:
    st.warning("⚠️ Nenhuma pergunta encontrada.")

# ➕ Formulário de edição/inserção
st.subheader("➕ Adicionar ou Editar Pergunta")

with st.form("form_crud"):
    id_edicao = st.session_state.get("edit_id", None)

    codigo_input = st.text_input(
        "Pergunta",
        value=st.session_state.get("edit_codigo", ""),
        help="Código identificador da pergunta"
    )
    descricao_input = st.text_area(
        "Texto",
        value=st.session_state.get("edit_descricao", ""),
        help="Descrição completa da pergunta"
    )

    enviar = st.form_submit_button("💾 Salvar")

if enviar:
    if not codigo_input.strip() or not descricao_input.strip():
        st.warning("⚠️ Código e descrição não podem estar vazios.")
    else:
        try:
            if id_edicao:
                db.update_pergunta(id_edicao, codigo_input, descricao_input)
                st.success("✅ Pergunta atualizada com sucesso!")

                if "edit_id" in st.session_state:
                    st.session_state["edit_id"] = None
            else:
                db.insert_pergunta(codigo_input, descricao_input)
                st.success("✅ Pergunta adicionada com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar pergunta: {e}")
        finally:
            if "edit_codigo" in st.session_state:
                st.session_state["edit_codigo"] = ""
            if "edit_descricao" in st.session_state:
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

