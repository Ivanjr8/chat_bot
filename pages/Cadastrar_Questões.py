# app.py
import streamlit as st
from db_connection import DatabaseConnection
from decoradores import acesso_restrito

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

    
# Proteção com Redirect
if "perfil" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.switch_page("gemini.py")

# Proteção básica
if "perfil" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()
    
@acesso_restrito(id_modulo=1)
def render():
    st.title("🤖 Chatbot")
    st.write("Conteúdo restrito aos perfis autorizados.")
    

# 🔍 Filtros
filtros = db.get_filtros_perguntas()
modulo_opcoes = ["Todos"] + filtros["modulos"]
disciplina_opcoes = [{"id": None, "nome": "Todas"}] + filtros["disciplinas"]
descritor_opcoes = [{"id": None, "tipo": "Todos"}] + filtros["descritores"]

col1, col2, col3 = st.columns(3)
with col1:
    modulo_selecionado = st.selectbox("🔎 Numero da Questão", options=modulo_opcoes)
with col2:
    disciplina_selecionada = st.selectbox("📘 Disciplina", options=disciplina_opcoes, format_func=lambda x: x["nome"])
with col3:
    descritor_selecionado = st.selectbox("🧩 Tipo de Descritor", options=descritor_opcoes, format_func=lambda x: x["tipo"])

filtro_modulo = None if modulo_selecionado == "Todos" else modulo_selecionado
filtro_disciplina = disciplina_selecionada["id"]
filtro_descritor = descritor_selecionado["id"]

perguntas = db.get_perguntas(filtro_modulo, filtro_disciplina, filtro_descritor)

# ➕ Formulário
st.subheader("➕ Adicionar ou Editar Pergunta")
with st.form("form_crud"):
    id_edicao = st.session_state.get("edit_id", None)

    titulo_input = st.text_input("Pergunta", value=st.session_state.get("edit_titulo", ""))
    descricao_input = st.text_area("Descrição", value=st.session_state.get("edit_descricao", ""))

    disciplina_input = st.selectbox("Disciplina", options=filtros["disciplinas"], format_func=lambda x: x["nome"],
                                    index=next((i for i, d in enumerate(filtros["disciplinas"]) if d["id"] == st.session_state.get("edit_disciplina")), 0))
    descritor_input = st.selectbox("Tipo de Descritor", options=filtros["descritores"], format_func=lambda x: x["tipo"],
                                   index=next((i for i, d in enumerate(filtros["descritores"]) if d["id"] == st.session_state.get("edit_descritor")), 0))

    enviar = st.form_submit_button("💾 Salvar")

if enviar:
    if not titulo_input.strip() or not descricao_input.strip():
        st.warning("⚠️ Título e descrição são obrigatórios.")
    else:
        try:
            if id_edicao:
                db.update_pergunta(id_edicao, titulo_input, descricao_input, disciplina_input["id"], descritor_input["id"])
                st.success("✅ Pergunta atualizada com sucesso!")
            else:
                db.insert_pergunta(titulo_input, descricao_input, disciplina_input["id"], descritor_input["id"])
                st.success("✅ Pergunta adicionada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
        finally:
            for key in ["edit_id", "edit_titulo", "edit_descricao", "edit_disciplina", "edit_descritor"]:
                st.session_state.pop(key, None)
            st.rerun()

# 📋 Visualização
st.subheader(f"📋 {len(perguntas)} pergunta(s) encontrada(s)")
for row in perguntas:
    id_pergunta = row.get('PK_CO_PERGUNTA')
    titulo = row.get('NO_PERGUNTA', '').strip()
    descricao = row.get('DE_PERGUNTA', '').strip()
    disciplina = row.get('NO_DISCIPLINA', '').strip()
    tipo_descritor = row.get('CO_TIPO', '').strip()

    with st.expander(f"📝 {titulo}"):
        st.markdown(f"**Descrição:** {descricao}  \n**Disciplina:** {disciplina}  \n**Tipo de Descritor:** {tipo_descritor}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Editar", key=f"editar_{id_pergunta}"):
                st.session_state["edit_id"] = id_pergunta
                st.session_state["edit_titulo"] = titulo
                st.session_state["edit_descricao"] = descricao
                st.session_state["edit_disciplina"] = next((d["id"] for d in filtros["disciplinas"] if d["nome"] == disciplina), None)
                st.session_state["edit_descritor"] = next((d["id"] for d in filtros["descritores"] if d["tipo"] == tipo_descritor), None)
                st.rerun()

        with col2:
            if st.button("❌ Excluir", key=f"excluir_{id_pergunta}"):
                st.session_state["confirm_delete_id"] = id_pergunta
                st.rerun()

    if st.session_state.get("confirm_delete_id") == id_pergunta:
        st.warning(f"⚠️ Confirmar exclusão da pergunta: **{titulo}**")
        confirmar, cancelar = st.columns(2)
        with confirmar:
            if st.button("✅ Confirmar", key=f"confirmar_{id_pergunta}"):
                db.delete_pergunta(id_pergunta)
                st.success("Pergunta excluída com sucesso.")
                st.session_state.pop("confirm_delete_id", None)
                st.rerun()
        with cancelar:
            if st.button("🚫 Cancelar", key=f"cancelar_{id_pergunta}"):
                st.session_state.pop("confirm_delete_id", None)
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

