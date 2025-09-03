import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from db_connection import DatabaseConnection
from decoradores import acesso_restrito


# 🎯 Configuração da página
st.set_page_config(page_title="Gestão de Acessos e Módulos", page_icon="🔐", layout="wide")
st.title("🔐 Painel de Configuração de Acesso")

# 🔧 Estilo personalizado
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Arquivo de estilo não encontrado.")
   

# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()
conn = db.conn

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()

# 🔌 Conexão via SQLAlchemy
engine = create_engine(
    f"mssql+pyodbc://{st.secrets['database']['uid']}:{st.secrets['database']['pwd']}@"
    f"{st.secrets['database']['server']}/{st.secrets['database']['database']}?"
    f"driver=ODBC+Driver+17+for+SQL+Server"
)


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
            
if conn and engine:
    cursor = conn.cursor()

    # 📦 Módulos existentes
    st.subheader("📦 Módulos Existentes")
    modulos_df = pd.read_sql("SELECT id_modulo, nome_modulo, caminho_pagina FROM TB_011_MODULOS", engine)
    st.dataframe(modulos_df, use_container_width=True)

    # ➕ Adicionar novo módulo
    st.subheader("➕ Adicionar Novo Módulo")
    with st.form("form_novo_modulo"):
        novo_nome = st.text_input("Nome do módulo")
        novo_caminho = st.text_input("Caminho da página")
        submitted = st.form_submit_button("Adicionar módulo")

        if submitted:
            if not novo_nome.strip() or not novo_caminho.strip():
                st.warning("⚠️ Nome e caminho não podem estar vazios.")
            elif novo_nome.lower() in modulos_df["nome_modulo"].str.lower().values:
                st.warning("⚠️ Já existe um módulo com esse nome.")
            else:
                try:
                    cursor.execute("""
                        INSERT INTO TB_011_MODULOS (nome_modulo, caminho_pagina)
                        VALUES (?, ?)
                    """, novo_nome.strip(), novo_caminho.strip())
                    conn.commit()
                    st.success(f"✅ Módulo '{novo_nome}' adicionado com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro ao adicionar módulo: {e}")

    # 🔧 Configurar acessos
    st.subheader("🔧 Configurar Acessos por Usuário")

    query_acesso = """
    SELECT 
        u.usuario,
        u.perfil,
        m.id_modulo,
        m.nome_modulo,
        CASE 
            WHEN a.perfil = LOWER(u.perfil) THEN 1
            ELSE 0
        END AS acesso
    FROM TB_010_USUARIOS u
    CROSS JOIN TB_011_MODULOS m
    LEFT JOIN TB_012_ACESSOS a 
        ON LOWER(u.perfil) = a.perfil AND m.id_modulo = a.id_modulo
    ORDER BY u.usuario, m.id_modulo;
    """
    df_acesso = pd.read_sql(query_acesso, engine)

    usuario_selecionado = st.selectbox("Filtrar por usuário", options=["Todos"] + sorted(df_acesso["usuario"].unique()))
    if usuario_selecionado != "Todos":
        df_acesso = df_acesso[df_acesso["usuario"] == usuario_selecionado]

    st.write("🟢 Marque os módulos que o usuário pode acessar:")
    acessos_atualizados = []

    for usuario in df_acesso["usuario"].unique():
        if usuario_selecionado != "Todos" and usuario != usuario_selecionado:
            continue

        st.markdown(f"**👤 Usuário: {usuario}**")
        usuario_df = df_acesso[df_acesso["usuario"] == usuario]

        for _, row in usuario_df.iterrows():
            modulo = row["nome_modulo"]
            perfil = row["perfil"].lower()
            id_modulo = row["id_modulo"]
            acesso_atual = bool(row["acesso"])

            chave_id = f"{usuario}_{perfil}_{id_modulo}"
            chave = st.toggle(f"🔌 {modulo}", value=acesso_atual, key=chave_id)
            acessos_atualizados.append({
                "perfil": perfil,
                "id_modulo": id_modulo,
                "acesso": chave
            })

    # 💾 Botão para salvar acessos
    if st.button("💾 Salvar Acessos"):
        db.salvar_acessos(acessos_atualizados, df_acesso)
        
db.close()

