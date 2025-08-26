import streamlit as st
import pyodbc
import random


# Função de conexão
def conectar_banco():
    try:
        conexao = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=myfreesqldbserver-0101.database.windows.net;"
            "DATABASE=myFreeDB;"
            "UID=ivan;"  # substitua pelo seu usuário real
            "PWD=MigMat01#!;"  # substitua pela sua senha real
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return conexao
    except Exception as erro:
        st.error(f"❌ Erro ao conectar: {erro}")
        return None

# Função para gerar um único INSERT aleatório
def gerar_insert_unico():
    perguntas_exemplo = [
        "Qual é a capital do Brasil?",
        "O que é um algoritmo?",
        "Quem descobriu o Brasil?",
        "O que significa HTML?",
        "Qual linguagem estiliza páginas web?",
        "O que é uma variável?",
        "Qual a função do comando SELECT?",
        "O que representa o número pi?",
        "Qual a diferença entre RAM e HD?",
        "Em que ano foi a independência do Brasil?"
    ]
    pergunta = random.choice(perguntas_exemplo).replace("'", "''")
    fk_modulo = random.randint(100, 105)
    id = random.randint(1000, 9999)  # ID aleatório para evitar conflito
    sql = f"INSERT INTO [dbo].[SimuladoPerguntas] ([id], [pergunta], [FK_MODULO]) VALUES ({id}, '{pergunta}', {fk_modulo});"
    return sql

# Interface Streamlit
st.set_page_config(page_title="Conexão com Banco", page_icon="🗄️", layout="centered")
st.title("🗄️ Conexão com SQL Server")

st.markdown("Clique no botão abaixo para conectar e listar as tabelas disponíveis:")

if st.button("🔌 Conectar ao Banco"):
    conexao = conectar_banco()
    
    if conexao:
        st.success("✅ Conexão bem-sucedida com o banco de dados!")
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT name FROM sys.tables")
            tabelas = cursor.fetchall()

            if tabelas:
                st.subheader("📂 Tabelas encontradas:")
                for tabela in tabelas:
                    st.markdown(f"- **{tabela.name}**")

                # Geração de INSERT único
                st.subheader("🧪 Gerar um único INSERT aleatório para SimuladoPerguntas")
                if st.button("🎲 Gerar INSERT"):
                    insert_sql = gerar_insert_unico()
                    st.code(insert_sql, language="sql")
            else:
                st.info("Nenhuma tabela encontrada no banco.")
        except Exception as erro:
            st.error(f"Erro ao buscar dados: {erro}")
        finally:
            conexao.close()
    else:
        st.warning("Não foi possível estabelecer conexão.")