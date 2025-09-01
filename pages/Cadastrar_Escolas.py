import streamlit as st
from db_connection import DatabaseConnection
#from db_connection1 import (buscar_escolas)
from decoradores import acesso_restrito
import math


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
    
@acesso_restrito(id_modulo=5)
def render():
    st.title("🗂️ Cadastrar_Escolas")
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
        ordem_personalizada = [1, 2, 3, 4, 5, 6, 7, 9, 97, 98, 99]
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

# 🔧 Inicialização do estado
def inicializar_estado():
    for k in ["mensagem_sucesso", "limpar_campos", "filtro_nome", "pagina_atual", "novo_id_escola", "novo_nome_escola"]:
        if k not in st.session_state:
            st.session_state[k] = "" if k != "pagina_atual" else 1

# 🧹 Limpa campos após cadastro ou atualização
def limpar_campos():
    st.session_state.novo_id_escola = ""
    st.session_state.novo_nome_escola = ""
    st.session_state.limpar_campos = False

# ✅ Exibe mensagem de sucesso
def exibir_mensagem():
    if st.session_state.mensagem_sucesso:
        st.success(st.session_state.mensagem_sucesso)
        st.session_state.mensagem_sucesso = ""

# ➕ Cadastro de nova escola
def cadastrar_escola():
    st.subheader("➕ Adicionar nova escola")
    st.text_input("ID da nova escola", key="novo_id_escola")
    st.text_input("Nome da nova escola", key="novo_nome_escola")
 
    
    if st.button("✅ Cadastrar"):
        id_escola = st.session_state.novo_id_escola.strip()
        nome = st.session_state.novo_nome_escola.strip()

        if id_escola and nome:
            if db.get_escola_por_id(id_escola):
                st.error("❌ Já existe uma escola com esse ID.")
            else:
                db.insert_escola(id_escola, nome)
                if db.get_escola_por_id(id_escola):
                  st.error("❌ Erro ao cadastrar escola.")
                  st.rerun()
                else:
                  
                  st.session_state.mensagem_sucesso = f"Escola Cadastrada com sucesso!"
                  st.session_state.limpar_campos = True
                  st.rerun() 
        else:
            st.error("❌ Preencha todos os campos.")

# 🔍 Filtro por nome
def aplicar_filtro():
    busca = st.text_input("🔍 Buscar escola por nome")
    if busca:
        st.session_state.filtro_nome = busca
        
        

# 📋 Listagem com paginação
def listar_escolas():
    escolas = db.get_escolas(st.session_state.filtro_nome)
    total = len(escolas)
    por_pagina = 15
    total_paginas = max(1, math.ceil(total / por_pagina))
    pagina = st.session_state.pagina_atual

    # Navegação
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Anterior") and pagina > 1:
            st.session_state.pagina_atual -= 1
            st.rerun()
    with col3:
        if st.button("➡️ Próxima") and pagina < total_paginas:
            st.session_state.pagina_atual += 1
            st.rerun()
    with col2:
        st.markdown(f"<center>Página {pagina} de {total_paginas}</center>", unsafe_allow_html=True)

    # Escolas da página atual
    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    escolas_pagina = escolas[inicio:fim]

    if not escolas_pagina:
        st.warning("Nenhuma escola encontrada.")
    else:
        for idx, escola in enumerate(escolas_pagina):
            exibir_escola(escola, idx)

# 🛠️ Atualizar ou excluir escola
def exibir_escola(escola, idx):
    with st.expander(f"📘 {escola['NO_ESCOLA']}"):
        atualizar_id = st.checkbox("Atualizar ID", key=f"check_id_{idx}")
        atualizar_nome = st.checkbox("Atualizar nome", key=f"check_nome_{idx}")

        novo_id = st.text_input("Novo ID", value=escola['PK_ID_ESCOLA'], key=f"id_{idx}")
        novo_nome = st.text_input("Novo nome", value=escola['NO_ESCOLA'], key=f"nome_{idx}")

        col1, col2, _ = st.columns(3)
        with col1:
            if st.button("💾 Atualizar", key=f"update_{idx}"):
                id_atual = escola['PK_ID_ESCOLA']
                if not atualizar_id and not atualizar_nome:
                    st.warning("⚠️ Marque ao menos um campo para atualizar.")
                elif (atualizar_id and not novo_id.strip()) or (atualizar_nome and not novo_nome.strip()):
                    st.warning("⚠️ Preencha os campos marcados para atualização.")
                elif atualizar_id and novo_id != id_atual and db.get_escola_por_id(novo_id):
                    st.error("❌ Já existe uma escola com esse novo ID.")
                else:
                    id_final = novo_id.strip() if atualizar_id else id_atual
                    nome_final = novo_nome.strip() if atualizar_nome else escola['NO_ESCOLA']
                    sucesso = db.update_escola(id_atual, id_final, nome_final)
                    if sucesso:
                        st.session_state.mensagem_sucesso = f"Escola '{escola['NO_ESCOLA']}' excluída com sucesso!"
                        st.session_state.limpar_campos = True
                        st.rerun()
                        
                    else:
                        st.error("❌ Erro ao atualizar.")
                       

        with col2:
            excluir = st.checkbox(f"Confirmar exclusão da escola '{escola['NO_ESCOLA']}'", key=f"confirm_delete_{idx}")
            if st.button("🗑️ Excluir", key=f"delete_{idx}"):
                if excluir:
                    sucesso = db.delete_escola(escola['PK_ID_ESCOLA'])
                    if sucesso:
                        st.error("❌ Erro ao excluir.")
                    else:
                        st.session_state.mensagem_sucesso = f"Escola '{escola['NO_ESCOLA']}' excluída com sucesso!"
                        st.session_state.limpar_campos = True
                        st.rerun()
                        
                else:
                    st.warning("⚠️ Marque a caixa para confirmar a exclusão.")

# 🚀 Execução principal
inicializar_estado()
if st.session_state.limpar_campos:
    limpar_campos()
exibir_mensagem()
cadastrar_escola()
aplicar_filtro()
listar_escolas()


st.markdown("---")
db.close()
