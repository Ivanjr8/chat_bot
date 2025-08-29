import streamlit as st
import pandas as pd
from database import DatabaseConnection

# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()

st.title("🔐 Gerenciar Matriz de Acesso")

# 📦 Query SQL
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

# 📊 Carregar dados
df = pd.read_sql(query, db.connect())

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



db.close()