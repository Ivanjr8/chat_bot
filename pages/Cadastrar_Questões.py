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

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()
    
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

# Conteúdo após login
# 🔧 Estilo personalizado
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil

# 🔍 Função para buscar acessos permitidos
def buscar_acessos_permitidos(perfil):
    try:
        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT id_modulo FROM TB_012_ACESSOS WHERE LOWER(perfil) = ?",
            (perfil,)
        )
        
        # 🔽 Aqui entra sua ordenação personalizada
        ordem_personalizada = [1, 2, 3, 4, 5, 6, 7, 9, 10, 97, 98, 99]
        modulos_permitidos = [row[0] for row in cursor.fetchall()]
        modulos_ordenados = [mod for mod in ordem_personalizada if mod in modulos_permitidos]
        
        return modulos_ordenados

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
    10: {"label": "🗂️   Professores", "page": "pages/Cadastrar_Professores.py", "key": "btn_ Cadastrar_Professores"},
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



