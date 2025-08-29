import streamlit as st
from db_connection import DatabaseConnection
from decoradores import acesso_restrito

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

# Proteção para acesso não autorizado
@acesso_restrito(id_modulo=5)
def pagina_matriz():
    st.write("Bem-vindo à área de gestão da matriz. Aqui estão os dados estratégicos.")
pagina_matriz() 

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
    5: {"label": "🗂️   Cadastrar Escolas", "page": "pages/Cadastrar_Escolas.py", "key": "btn_escolas"},
    9: {"label": "🗂️   Cadastrar Usuarios", "page": " pages/Cadastrar_Usuarios.py", "key": "btn_ Cadastrar_Usuarios"},
}
botoes_admin = {
    6: {"label": "🗂️   matriz", "page": "pages/matriz.py", "key": "btn_matriz"},
    7: {"label": "✅   Teste de  Conexão", "page": "pages/conn_azure.py", "key": "conn_azure.py"},
    
}
botoes_retornar = {
    99: {"label": "↩️   Retornar", "page": "gemini.py", "key": "btn_retornar"},  # acesso universal
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
        st.markdown("### 📞   Suporte")
        st.write("Email: suporte@meuapp.com")

        # 🚪 Botão para sair
        if st.button("🚪 Sair"):
            for key in ["usuario", "perfil", "usuario_id"]:
                st.session_state.pop(key, None)
            st.switch_page("gemini.py")
            st.rerun()
            
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
