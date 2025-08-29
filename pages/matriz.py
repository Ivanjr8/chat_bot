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

# 🔌 Conexão via SQLAlchemy
engine = create_engine(
    f"mssql+pyodbc://{st.secrets['database']['uid']}:{st.secrets['database']['pwd']}@"
    f"{st.secrets['database']['server']}/{st.secrets['database']['database']}?"
    f"driver=ODBC+Driver+17+for+SQL+Server"
)

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

