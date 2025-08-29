import streamlit as st
import pandas as pd
import pyodbc

# 🔌 Função de conexão
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
st.set_page_config(page_title="Matriz de Acesso", layout="wide")
st.title("🔐 Matriz de Acesso por Perfil")

# 📡 Conectar ao banco
conn = conectar_banco()
if conn:
    query = """
    SELECT 
        u.usuario,
        u.perfil,
        m.nome_modulo,
        CASE 
            WHEN a.perfil = LOWER(u.perfil) THEN 'ok'
            ELSE 'não ok'
        END AS acesso
    FROM [dbo].[TB_010_USUARIOS] u
    CROSS JOIN [dbo].[TB_011_MODULOS] m
    LEFT JOIN [dbo].[TB_012_ACESSOS] a 
        ON LOWER(u.perfil) = a.perfil AND m.id_modulo = a.id_modulo
    ORDER BY u.usuario, m.id_modulo;
    """
    
    df = pd.read_sql(query, conn)

    # 🧮 Pivotar para matriz
    matriz = df.pivot_table(index=["usuario", "perfil"], 
                            columns="nome_modulo", 
                            values="acesso", 
                            aggfunc="first").fillna("não ok")

    # 🎛️ Filtro por perfil
    perfil_selecionado = st.selectbox("Filtrar por perfil", options=["Todos"] + sorted(df["perfil"].unique()))
    if perfil_selecionado != "Todos":
        matriz = matriz.loc[matriz.index.get_level_values("perfil") == perfil_selecionado]

    # 📋 Exibir matriz
    st.dataframe(matriz, use_container_width=True)
