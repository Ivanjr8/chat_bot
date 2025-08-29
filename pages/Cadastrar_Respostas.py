import streamlit as st
from db_connection import DatabaseConnection

# 🔧 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Configuração da Página
st.set_page_config(page_title="📚 CRUD Respostas", layout="wide")
# Titulo da página
st.title("📝 Cadastro de Respostas")

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

# 🔍 Filtros
st.subheader("🔍 Filtrar por Questão, Disciplina e Descritor")

filtros = db.get_filtros_perguntas()
modulo_opcoes = ["Todos"] + filtros["modulos"]
disciplina_opcoes = [{"id": None, "nome": "Todas"}] + filtros["disciplinas"]
descritor_opcoes = [{"id": None, "tipo": "Todos"}] + filtros["descritores"]

col1, col2, col3 = st.columns(3)
with col1:
    modulo_selecionado = st.selectbox("🔎 Número da Questão", options=modulo_opcoes)
with col2:
    disciplina_selecionada = st.selectbox("📘 Disciplina", options=disciplina_opcoes, format_func=lambda x: x["nome"])
with col3:
    descritor_selecionado = st.selectbox("🧩 Tipo de Descritor", options=descritor_opcoes, format_func=lambda x: x["tipo"])

filtro_modulo = None if modulo_selecionado == "Todos" else modulo_selecionado
filtro_disciplina = disciplina_selecionada.get("id")
filtro_descritor = descritor_selecionado.get("id")

respostas = db.get_respostas_com_filtros(filtro_modulo, filtro_disciplina, filtro_descritor)

if not respostas:
    st.warning("Nenhuma resposta encontrada com os filtros selecionados.")

# ➕ Cadastro de múltiplas respostas
st.subheader("➕ Adicionar 4 Respostas para uma Pergunta")

perguntas = db.get_perguntas() or []
if perguntas:
    pergunta_opcoes = {f"{p['PK_CO_PERGUNTA']} - {p['NO_PERGUNTA'].strip()}": p['PK_CO_PERGUNTA'] for p in perguntas}
    pergunta_selecionada = st.selectbox("Pergunta relacionada", list(pergunta_opcoes.keys()))
    pergunta_id = pergunta_opcoes.get(pergunta_selecionada)
else:
    st.warning("⚠️ Nenhuma pergunta disponível.")
    pergunta_id = None

with st.form("form_respostas_multiplas"):
    respostas_input = []
    for i in range(1, 5):
        st.markdown(f"**Resposta {i}**")
        texto = st.text_input(f"Texto da Resposta {i}", key=f"texto_{i}")
        alternativa = st.text_input(f"Letra da Alternativa {i}", value=chr(64+i), key=f"alt_{i}")
        correta = st.checkbox("É a resposta correta?", key=f"correta_{i}")
        respostas_input.append({
            "texto": texto,
            "alternativa": alternativa,
            "correta": correta
        })

    enviar = st.form_submit_button("💾 Salvar todas")

if enviar:
    respostas_invalidas = [r for r in respostas_input if not r["texto"].strip()]
    respostas_corretas = [r for r in respostas_input if r["correta"]]

    if not pergunta_id:
        st.warning("⚠️ Selecione uma pergunta.")
    elif respostas_invalidas:
        st.warning("⚠️ Todas as respostas devem ter texto preenchido.")
    elif len(respostas_corretas) != 1:
        st.warning("⚠️ Deve haver exatamente uma resposta marcada como correta.")
    else:
        try:
            for r in respostas_input:
                db.insert_resposta_completa(
                    texto=r["texto"].strip(),
                    alternativa=r["alternativa"].strip(),
                    pergunta_id=pergunta_id,
                    correta=r["correta"]
                )
            st.success("✅ Respostas adicionadas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {e}")

# 📋 Listagem de respostas
st.subheader(f"📋 {len(respostas)} resposta(s) encontrada(s)")

for i, r in enumerate(respostas):
    id_resposta = r.get('co_resposta') or f"na_{i}"
    texto = (r.get('no_resposta') or '').strip()
    alternativa = (r.get('no_alternativa') or '').strip()
    correta = r.get('co_resposta_correta', False)
    pergunta = (r.get('no_pergunta') or '').strip()
    disciplina = (r.get('no_disciplina') or '').strip()
    descritor = (r.get('co_tipo') or '').strip()

    with st.expander(f"{alternativa}) {texto}"):
        st.markdown(f"""
        **Pergunta:** {pergunta}  
        **Disciplina:** {disciplina}  
        **Descritor:** {descritor}  
        **Alternativa:** {alternativa}  
        **Correta:** {'✅ Sim' if correta else '❌ Não'}
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Editar", key=f"edit_{id_resposta}_{i}"):
                st.session_state["edit_id"] = id_resposta
                st.session_state["edit_texto"] = texto
                st.session_state["edit_alternativa"] = alternativa
                st.session_state["edit_correta"] = correta
                st.rerun()

        with col2:
            if st.button("❌ Excluir", key=f"del_{id_resposta}_{i}"):
                st.session_state["confirm_delete_id"] = id_resposta
                st.rerun()

    if st.session_state.get("confirm_delete_id") == id_resposta:
        st.warning(f"⚠️ Confirmar exclusão da resposta: **{texto}**")
        confirmar, cancelar = st.columns(2)
        with confirmar:
            if st.button("✅ Confirmar", key=f"confirma_{id_resposta}_{i}"):
                db.delete_resposta(id_resposta)
                st.success("Resposta excluída com sucesso.")
                st.session_state.pop("confirm_delete_id", None)
                st.rerun()
        with cancelar:
            if st.button("🚫 Cancelar", key=f"cancela_{id_resposta}_{i}"):
                st.session_state.pop("confirm_delete_id", None)
                st.rerun()

# ✏️ Edição de resposta
if "edit_id" in st.session_state:
    st.subheader("✏️ Editar Resposta")
    with st.form("form_editar_resposta"):
        novo_texto = st.text_input("Texto da resposta", value=st.session_state["edit_texto"])
        nova_alternativa = st.text_input("Letra da alternativa", value=st.session_state["edit_alternativa"])
        nova_correta = st.checkbox("É a resposta correta?", value=st.session_state["edit_correta"])
        salvar_edicao = st.form_submit_button("💾 Atualizar")

    if salvar_edicao:
        try:
            db.update_resposta_completa(
                id_resposta=st.session_state["edit_id"],
                texto=novo_texto.strip(),
                alternativa=nova_alternativa.strip(),
                correta=nova_correta
            )
            st.success("✅ Resposta atualizada com sucesso!")
            for key in ["edit_id", "edit_texto", "edit_alternativa", "edit_correta"]:
                st.session_state.pop(key, None)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao atualizar: {e}")

db.close()
