import streamlit as st
import pandas as pd
import pyodbc
from sqlalchemy import create_engine

# 🔌 Conexão com o banco via SQLAlchemy
def conectar_engine():
    try:
        engine = create_engine(
            "mssql+pyodbc://ivan:MigMat01#!@srvappmba.database.windows.net/MBA-APP?driver=ODBC+Driver+17+for+SQL+Server"
        )
        return engine
    except Exception as erro:
        st.error(f"❌ Erro ao conectar via SQLAlchemy: {erro}")
        return None

# 🔌 Conexão direta para execução de comandos
def conectar_banco():
    try:
        conexao = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=srvappmba.database.windows.net;"
            "DATABASE=MBA-APP;"
            "UID=ivan;"
            "PWD=MigMat01#!;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return conexao
    except Exception as erro:
        st.error(f"❌ Erro ao conectar: {erro}")
        return None

# 🛠 Função para salvar acessos
def salvar_acessos(acessos_atualizados, df_acesso, cursor, conn):
    if not acessos_atualizados:
        st.warning("⚠️ Nenhuma alteração de acesso foi feita.")
        return

    erros = []
    perfis_validos = set(df_acesso["perfil"].str.lower().str.strip().unique())

    for item in acessos_atualizados:
        perfil = item.get("perfil", "").strip().lower()
        id_modulo = item.get("id_modulo")
        acesso = item.get("acesso", False)

        if perfil not in perfis_validos:
            erros.append(f"❌ Perfil inválido: {perfil}")
            continue

        try:
            if acesso:
                cursor.execute("""
                    SELECT 1 FROM TB_012_ACESSOS WHERE LOWER(perfil) = ? AND id_modulo = ?
                """, perfil, id_modulo)
                existe = cursor.fetchone()

                if not existe:
                    cursor.execute("""
                        INSERT INTO TB_012_ACESSOS (perfil, id_modulo)
                        VALUES (?, ?)
                    """, perfil, id_modulo)
            else:
                st.write(f"Tentando deletar: perfil={perfil}, id_modulo={id_modulo}")
                cursor.execute("""
                    DELETE FROM TB_012_ACESSOS WHERE LOWER(perfil) = ? AND id_modulo = ?
                """, perfil, id_modulo)

        except Exception as e:
            erros.append(f"❌ Erro ao atualizar acesso de {perfil} ao módulo {id_modulo}: {e}")

    if erros:
        for erro in erros:
            st.warning(erro)
    else:
        try:
            conn.commit()
            st.success("✅ Acessos atualizados com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar alterações no banco: {e}")

# 🎯 Configuração da página
st.set_page_config(page_title="Gestão de Acessos e Módulos", layout="wide")
st.title("🔐 Painel de Configuração de Acesso")

conn = conectar_banco()
engine = conectar_engine()

if conn and engine:
    cursor = conn.cursor()

    # 🔹 Exibir módulos existentes
    st.subheader("📦 Módulos Existentes")
    modulos_df = pd.read_sql("SELECT id_modulo, nome_modulo, caminho_pagina FROM TB_011_MODULOS", engine)
    st.dataframe(modulos_df, width='stretch')

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
    st.subheader("🔧 Configurar Acessos por Perfil")

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

    perfil_selecionado = st.selectbox("Filtrar por perfil", options=["Todos"] + sorted(df_acesso["perfil"].unique()))
    if perfil_selecionado != "Todos":
        df_acesso = df_acesso[df_acesso["perfil"] == perfil_selecionado]

    st.write("🟢 Marque os módulos que o perfil pode acessar:")
    acessos_atualizados = []

    for usuario in df_acesso["usuario"].unique():
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

    if st.button("💾 Salvar Acessos"):
        salvar_acessos(acessos_atualizados, df_acesso, cursor, conn)