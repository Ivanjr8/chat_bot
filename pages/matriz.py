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
st.title("🔐 Painel de Configuração de Acesso")

conn = conectar_banco()
if conn:
    cursor = conn.cursor()

    # 🔹 Exibir módulos existentes
    st.subheader("📦 Módulos Existentes")
    modulos_df = pd.read_sql("SELECT id_modulo, nome_modulo, caminho_pagina FROM TB_011_MODULOS", conn)
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
                    st.rerun()
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
    df_acesso = pd.read_sql(query_acesso, conn)

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

    # 💾 Salvar acessos
    if st.button("💾 Salvar Acessos"):
        erros = []
        perfis_validos = set(df_acesso["perfil"].str.lower().unique())

        for item in acessos_atualizados:
            perfil = item["perfil"]
            id_modulo = item["id_modulo"]
            acesso = item["acesso"]

            if perfil.lower() not in perfis_validos:
                erros.append(f"❌ Perfil inválido: {perfil}")
                continue

            try:
                if acesso:
                    cursor.execute("""
                        IF NOT EXISTS (
                            SELECT 1 FROM TB_012_ACESSOS WHERE perfil = ? AND id_modulo = ?
                        )
                        INSERT INTO TB_012_ACESSOS (perfil, id_modulo)
                        VALUES (?, ?);
                    """, perfil, id_modulo, perfil, id_modulo)
                else:
                    cursor.execute("""
                        DELETE FROM TB_012_ACESSOS WHERE perfil = ? AND id_modulo = ?
                    """, perfil, id_modulo)
            except Exception as e:
                erros.append(f"Erro ao atualizar acesso de {perfil} ao módulo {id_modulo}: {e}")

        if erros:
            for erro in erros:
                st.warning(erro)
        else:
            conn.commit()
            st.success("✅ Acessos atualizados com sucesso!")