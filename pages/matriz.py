import streamlit as st
import pandas as pd
import pyodbc

# 🔌 Conexão com o banco
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

# 🎯 Configuração da página
st.set_page_config(page_title="Gestão de Acessos e Módulos", layout="wide")
st.title("🔐 Configuração de Acesso e Módulos")

conn = conectar_banco()
if conn:
    cursor = conn.cursor()

    # 🔹 Módulos editáveis
    st.subheader("📦 Editar Módulos")
    modulos_df = pd.read_sql("SELECT id_modulo, nome_modulo, caminho_pagina FROM TB_011_MODULOS", conn)
    modulos_editados = st.data_editor(modulos_df, num_rows="dynamic")

    if st.button("💾 Salvar Módulos"):
        erros = []
        nomes_existentes = set(modulos_df["nome_modulo"].str.lower())

        for _, row in modulos_editados.iterrows():
            id_modulo = row["id_modulo"]
            nome = str(row["nome_modulo"]).strip()
            caminho = str(row["caminho_pagina"]).strip()

            if not nome or not caminho:
                erros.append(f"❌ Módulo ID {id_modulo}: nome ou caminho vazio.")
                continue

            if nome.lower() in nomes_existentes and id_modulo not in modulos_df["id_modulo"].values:
                erros.append(f"⚠️ Módulo '{nome}' já existe.")
                continue

            cursor.execute("""
                MERGE TB_011_MODULOS AS alvo
                USING (SELECT ? AS id_modulo) AS origem
                ON alvo.id_modulo = origem.id_modulo
                WHEN MATCHED THEN
                    UPDATE SET nome_modulo = ?, caminho_pagina = ?
                WHEN NOT MATCHED THEN
                    INSERT (id_modulo, nome_modulo, caminho_pagina)
                    VALUES (?, ?, ?);
            """, id_modulo, nome, caminho, id_modulo, nome, caminho)

        if erros:
            for erro in erros:
                st.warning(erro)
        else:
            conn.commit()
            st.success("✅ Módulos atualizados com sucesso!")

    # 🔹 Matriz de acesso
    st.subheader("🔧 Editar Acessos por Perfil")
    query_acesso = """
    SELECT 
        u.usuario,
        u.perfil,
        m.id_modulo,
        m.nome_modulo,
        CASE 
            WHEN a.perfil = LOWER(u.perfil) THEN 'ok'
            ELSE 'não ok'
        END AS acesso
    FROM TB_010_USUARIOS u
    CROSS JOIN TB_011_MODULOS m
    LEFT JOIN TB_012_ACESSOS a 
        ON LOWER(u.perfil) = a.perfil AND m.id_modulo = a.id_modulo
    ORDER BY u.usuario, m.id_modulo;
    """
    df_acesso = pd.read_sql(query_acesso, conn)

    perfil_selecionado = st.selectbox("Filtrar por perfil", options=["Todos"] + sorted(df_acesso["perfil"].unique()))
    if perfil_selecionado != "Todos":
        df_acesso = df_acesso[df_acesso["perfil"] == perfil_selecionado]

    df_editado = st.data_editor(df_acesso, num_rows="dynamic")

    if st.button("💾 Salvar Acessos"):
        erros = []
        perfis_validos = {"admin", "professor", "aluno"}

        for _, row in df_editado.iterrows():
            perfil = str(row["perfil"]).strip().lower()
            id_modulo = row["id_modulo"]
            acesso = str(row["acesso"]).strip().lower()

            if perfil not in perfis_validos:
                erros.append(f"❌ Perfil inválido: {perfil}")
                continue

            if acesso == "ok":
                cursor.execute("""
                    IF NOT EXISTS (
                        SELECT 1 FROM TB_012_ACESSOS WHERE perfil = ? AND id_modulo = ?
                    )
                    INSERT INTO TB_012_ACESSOS (perfil, id_modulo)
                    VALUES (?, ?);
                """, perfil, id_modulo, perfil, id_modulo)
            elif acesso == "não ok":
                cursor.execute("""
                    DELETE FROM TB_012_ACESSOS WHERE perfil = ? AND id_modulo = ?
                """, perfil, id_modulo)
            else:
                erros.append(f"⚠️ Valor de acesso inválido: '{acesso}' para perfil {perfil}")

        if erros:
            for erro in erros:
                st.warning(erro)
        else:
            conn.commit()
            st.success("✅ Acessos atualizados com sucesso!")