import streamlit as st
import pandas as pd
import numpy as np
import time
from db_connection import DatabaseConnection
from decoradores import acesso_restrito

st.title("🔍 Buscar e Editar Professores")

# 🔧 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Configuração da Página
st.set_page_config(page_title="CRUD Professores", layout="wide")
# Titulo da página
st.title("🔄 Cadastro ou Atualização de Professores")

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
    st.title("🤖 Professores")
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

# Proteção com Redirect
if "perfil" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.switch_page("gemini.py")

# Proteção básica
if "perfil" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()



st.header("📚 Gerenciar Disciplinas")

filtro_disciplina = st.text_input("🔍 Digite parte do nome da disciplina")

if filtro_disciplina:
    resultados = db.buscar_disciplinas(filtro_disciplina)

    if resultados:
        df_disc = pd.DataFrame(resultados)
        st.dataframe(df_disc)

        nomes_disc = df_disc["NO_NOME_DISCIPLINA"].tolist()
        selecionado_disc = st.selectbox("Selecione uma disciplina", nomes_disc)

        if selecionado_disc:
            dados_disc = df_disc[df_disc["NO_NOME_DISCIPLINA"] == selecionado_disc].iloc[0]

            with st.form("form_edit_disciplina"):
                novo_nome_disc = st.text_input("Nome da disciplina", value=dados_disc["NO_NOME_DISCIPLINA"])
                
                atualizar_disc = st.form_submit_button("💾 Atualizar")
                excluir_disc = st.form_submit_button("🗑️ Excluir")

                if atualizar_disc:
                    db.connect()
                    cursor = db.conn.cursor()
                    cursor.execute("""
                        UPDATE TB_014_DISCIPLINAS
                        SET NO_NOME_DISCIPLINA = ?
                        WHERE PK_CO_DISCIPLINA = ?
                    """, (str(novo_nome_disc)))
                    db.conn.commit()
                    st.success("✅ Disciplina atualizada!")
                    time.sleep(2)
                    st.rerun()
                    db.close()

                if excluir_disc:
                    db.connect()
                    cursor = db.conn.cursor()
                    cursor.execute("""
                        DELETE FROM TB_014_DISCIPLINAS
                        WHERE NO_NOME_DISCIPLINA = ?
                    """, (selecionado_disc,))
                    db.conn.commit()
                    st.warning("🗑️ Disciplina excluída.")
                    time.sleep(2)
                    st.rerun()
                    db.close()
    else:
        st.info("🔎 Nenhuma disciplina encontrada com esse nome.")

st.header("➕ Cadastrar Nova Disciplina")

with st.form("form_nova_disciplina"):
    nome_disciplina = st.text_input("Nome da disciplina")
    cadastrar = st.form_submit_button("✅ Cadastrar")

    if cadastrar:
        if not nome_disciplina:
            st.warning("⚠️ Por favor, preencha o nome da disciplina.")
        else:
            try:
                db.connect()
                cursor = db.conn.cursor()
                cursor.execute("""
                    INSERT INTO TB_006_DISCIPLINA (NO_DISCIPLINA)
                    VALUES (?)
                """, (nome_disciplina,))
                db.conn.commit()
                st.success("🎉 Disciplina cadastrada com sucesso!")
                time.sleep(2)  # Espera 5 segundos
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar: {e}")
            finally:
                db.close()

