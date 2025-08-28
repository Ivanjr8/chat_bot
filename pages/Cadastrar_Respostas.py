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

# 🔍 Selecionar pergunta existente
perguntas = db.get_perguntas() or []

if perguntas:
    pergunta_opcoes = {}
    for p in perguntas:
        pk = p.get('PK_CO_PERGUNTA', 'ID desconhecido')
        titulo = p.get('NO_PERGUNTA', '').strip() if p.get('NO_PERGUNTA') else 'Pergunta sem título'
        label = f"{pk} - {titulo}"
        pergunta_opcoes[label] = pk

    pergunta_selecionada = st.selectbox("Pergunta relacionada", list(pergunta_opcoes.keys()))
    pergunta_id = pergunta_opcoes.get(pergunta_selecionada)
    st.markdown(f"**Pergunta selecionada:** {pergunta_selecionada}")
else:
    st.warning("⚠️ Nenhuma pergunta disponível para seleção.")
    pergunta_id = None

# ➕ Formulário de inserção de múltiplas respostas
st.subheader("➕ Adicionar 4 Respostas para a Pergunta Selecionada")

with st.form("form_respostas_multiplas"):
    respostas = []

    for i in range(1, 5):
        st.markdown(f"**Resposta {i}**")

        texto_key = f"texto_{i}"
        correta_key = f"correta_{i}"

        # Evita sobrescrever session_state
        if texto_key not in st.session_state:
            st.session_state[texto_key] = ""
        if correta_key not in st.session_state:
            st.session_state[correta_key] = False

        texto = st.text_input(f"Texto da Resposta {i}", key=texto_key)
        correta = st.checkbox("É a resposta correta?", key=correta_key)

        respostas.append({"texto": texto, "correta": correta})

    enviar = st.form_submit_button("💾 Salvar todas")

if enviar:
    # Validação de campos obrigatórios
    respostas_invalidas = [r for r in respostas if not r["texto"].strip()]
    respostas_corretas = [r for r in respostas if r["correta"]]

    if respostas_invalidas:
        st.warning("⚠️ Todas as respostas devem ter texto preenchido.")
    elif len(respostas_corretas) != 1:
        st.warning("⚠️ Deve haver exatamente uma resposta marcada como correta.")
    else:
        try:
            for r in respostas:
                db.insert_resposta(r["texto"].strip(), pergunta_id, r["correta"])
            st.success("✅ 4 respostas foram adicionadas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar respostas: {e}")

# 📋 Listar respostas existentes
respostas = db.get_respostas(pergunta_id) or []

st.subheader("📋 Respostas cadastradas")

if respostas:
    for r in respostas:
        # Proteção contra campos ausentes ou None
        id_resposta = r.get('CO_RESPOSTA', 'ID desconhecido')
        texto_resposta = r.get('NO_RESPOSTA', '').strip() or 'Sem texto'
        correta = r.get('CO_RESPOSTA_CORRETA', False)

        with st.expander(f"ID {id_resposta} - {texto_resposta}"):
            st.write(f"✔️ Correta: {'Sim' if correta else 'Não'}")

            col1, col2 = st.columns(2)

            with col1:
                editar_key = f"edit_{id_resposta}"
                if st.button(f"✏️ Editar", key=editar_key):
                    if "edit_id" not in st.session_state:
                        st.session_state["edit_id"] = id_resposta
                    if "edit_texto" not in st.session_state:
                        st.session_state["edit_texto"] = texto_resposta
                    if "edit_correta" not in st.session_state:
                        st.session_state["edit_correta"] = correta

            with col2:
                excluir_key = f"del_{id_resposta}"
                if st.button(f"❌ Excluir", key=excluir_key):
                    with st.modal(f"Tem certeza que deseja excluir a resposta {id_resposta}?"):
                        confirmar = st.button("Confirmar exclusão", key=f"confirma_{id_resposta}")
                        cancelar = st.button("Cancelar", key=f"cancela_{id_resposta}")

                        if confirmar:
                            db.delete_resposta(id_resposta)
                            st.success("Resposta excluída com sucesso.")
                            st.rerun()
                        elif cancelar:
                            st.info("Exclusão cancelada.")
else:
    st.warning("⚠️ Nenhuma resposta cadastrada para esta pergunta.")



db.close()