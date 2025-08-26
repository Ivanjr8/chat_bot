import streamlit as st
import pyodbc

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

                # Geração de INSERTs para SimuladoPerguntas
                st.subheader("📝 Gerar INSERTs da tabela SimuladoPerguntas")
                cursor.execute("SELECT TOP 10 [id], [pergunta], [FK_MODULO] FROM [dbo].[SimuladoPerguntas]")
                registros = cursor.fetchall()

                if registros:
                    inserts = []
                    for linha in registros:
                        id = linha.id
                        pergunta = linha.pergunta.replace("'", "''")  # Escapar aspas simples
                        fk = linha.FK_MODULO
                        sql = f"INSERT INTO [dbo].[SimuladoPerguntas] ([id], [pergunta], [FK_MODULO]) VALUES ({id}, '{pergunta}', {fk});"
                        inserts.append(sql)

                    st.code("\n".join(inserts), language="sql")
                else:
                    st.info("Nenhum registro encontrado na tabela SimuladoPerguntas.")
            else:
                st.info("Nenhuma tabela encontrada no banco.")
        except Exception as erro:
            st.error(f"Erro ao buscar dados: {erro}")
        finally:
            conexao.close()
    else:
        st.warning("Não foi possível estabelecer conexão.")