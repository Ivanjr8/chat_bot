import streamlit as st
from db_connection import DatabaseConnection
from decoradores import acesso_restrito

# 🔧 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Configuração da Página
st.set_page_config(page_title="📚 CRUD Respostas", layout="wide")
# Titulo da página
st.title("📝 Cadastro de Respostas")

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

# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()
    
# Conteúdo após login
# 🔧 Estilo personalizado
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil

# 🔍 Função para buscar acessos permitidos
def buscar_acessos_permitidos(perfil):
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT id_modulo FROM TB_012_ACESSOS WHERE LOWER(perfil) = ?", (perfil,))
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Erro ao buscar acessos: {e}")
        return []

# 🗺️ Mapeamento de módulos para botões e páginas
botoes_paginas = {
    1: {"label": "🎓   Chatbot", "page": "pages/chatbot.py", "key": "btn_chatbot"},
    2: {"label": "🖥️   Gerar Simulado", "page": "pages/Gerar_Simulado.py", "key": "btn_simulado"},
    
}
botoes_cadastro = {
    3: {"label": "🗂️   Questões", "page": "pages/Cadastrar_Questões.py", "key": "btn_cadastrar"},
    4: {"label": "🗂️   Respostas", "page": "pages/Cadastrar_Respostas.py", "key": "btn_cadastrar_respostas"},
    5: {"label": "🗂️   Escolas", "page": "pages/Cadastrar_Escolas.py", "key": "btn_escolas"},
    9: {"label": "🗂️   Usuários", "page": "pages/Cadastrar_Usuarios.py", "key": "btn_ Cadastrar_Usuarios"},
}
botoes_admin = {
    7: {"label": "✅   Teste de  Conexão", "page": "pages/conn_azure.py", "key": "conn_azure.py"},
    6: {"label": "🗂️   matriz", "page": "pages/matriz.py", "key": "btn_matriz"},
        
}
botoes_retornar = {
    99: {"label": "↩️   Retornar", "page": "gemini.py", "key": "btn_retornar"},  # acesso universal
}

botoes_link_aluno = {
    98: {
        "label": "📊   Painel do Aluno",
        "page": "https://app.powerbi.com/view?r=eyJrIjoiN2M2NWM1N2QtYWQ3My00NjM1LWFiMWQtMjg0YTIxMzMxNjNhIiwidCI6IjRhMjJmMTE2LTUxY2UtNGZlMy1hZWFhLTljNDYxNDNkMDg4YiJ9",
        "key": "btn_powerbi"
    }
}

botoes_link_professor = {
    97: {
        "label": "📊   Painel Professor",
        "page": "https://app.powerbi.com/view?r=eyJrIjoiYTAzMWJhZGYtMzI1ZS00MzkwLThiOGYtOGEwNWU4ZDUzMGVjIiwidCI6IjRhMjJmMTE2LTUxY2UtNGZlMy1hZWFhLTljNDYxNDNkMDg4YiJ9",
        "key": "btn_powerbi"
    }
}

# 🔧 Conteúdo após login
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil
    usuario = st.session_state.usuario

    modulos_permitidos = buscar_acessos_permitidos(perfil)
    
    # 👇 Adicione aqui para depurar
    #st.write("Modulos permitidos:", modulos_permitidos)
    #st.write("IDs disponíveis em botoes_cadastro:", list(botoes_cadastro.keys()))

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

        st.markdown("## ⚙️   Cadastro")

        for mod_id in modulos_permitidos:
            if mod_id in botoes_cadastro:
                btn = botoes_cadastro[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])

        st.markdown("## ⚙️   Administrativo")
        for mod_id in modulos_permitidos:
            if mod_id in botoes_admin:
                btn = botoes_admin[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])

        for mod_id in modulos_permitidos + [99]:
            if mod_id in botoes_retornar:
                btn = botoes_retornar[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])
        if perfil in ['Aluno', 'Administrador']:
            for mod_id in botoes_link_aluno:
                btn = botoes_link_aluno[mod_id]
                st.markdown("""
                <style>
                    .custom-btn {
                        background-color: #0000004c;
                        color: rgba(245, 245, 245, 0.849) !important;
                        text-align: left;
                        padding-left: 12px;
                        width: 240px;
                        height: 40px;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: background-color 0.3s ease-in-out;
                        display: flex;
                        justify-content: flex-start;
                        align-items: center;
                        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
                        transform: scale(1.02);
                        text-decoration: none !important;
                    }

                    .custom-btn:hover {
                        background-color: #10b981;
                        color: white;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <a href="{btn['page']}" target="_blank" class="custom-btn">
                    {btn['label']}
                </a>
            """, unsafe_allow_html=True)
         # 🎓 Botões exclusivos para Alunos
        if perfil != "Aluno":
            for mod_id in botoes_link_professor:
                btn = botoes_link_professor[mod_id]
                st.markdown("""
                <style>
                    .custom-btn {
                        background-color: #0000004c;
                        color: rgba(245, 245, 245, 0.849) !important;
                        text-align: left;
                        padding-left: 12px;
                        width: 240px;
                        height: 40px;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: background-color 0.3s ease-in-out;
                        display: flex;
                        justify-content: flex-start;
                        align-items: center;
                        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
                        transform: scale(1.02);
                        text-decoration: none !important;
                    }

                    .custom-btn:hover {
                        background-color: #10b981;
                        color: white;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <a href="{btn['page']}" target="_blank" class="custom-btn">
                    {btn['label']}
                </a>
            """, unsafe_allow_html=True)

        st.markdown("### 📞   Suporte")
        st.write("Email: suporte@meuapp.com")

        # 🚪 Botão para sair
        if st.button("🚪 Sair"):
            for key in ["usuario", "perfil", "usuario_id"]:
                st.session_state.pop(key, None)
            st.switch_page("gemini.py")
            st.rerun()  

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
