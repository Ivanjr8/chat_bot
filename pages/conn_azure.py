import streamlit as st
import pyodbc
from decoradores import acesso_restrito
from streamlit_modal import Modal
from db_connection import DatabaseConnection

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Configuração da Página
st.set_page_config(page_title="Conexão", layout="wide")
# Titulo da página
st.title("🔄 Restar Conexão com Banco de Dados")


# Conexão com o banco
db = DatabaseConnection()
db.connect()

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()
   
    
# Função de conexão
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
    st.title("🤖 Chatbot")
    st.write("Conteúdo restrito aos perfis autorizados.")
    
# Executando dentro do Streamlit
def executar_insert():
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            sql = "INSERT INTO [dbo].[SimuladoPerguntas] ([pergunta], [FK_MODULO]) VALUES ('quem descobriu a beringela', 1010);"
            cursor.execute(sql)
            conexao.commit()
            st.success("✅ INSERT executado com sucesso!")

            # Verificando se foi inserido
            cursor.execute("SELECT top 1 * FROM [dbo].[SimuladoPerguntas] order by id desc")
            resultado = cursor.fetchone()
            if resultado:
                st.write("📌 Resultado do SELECT:")
                st.write(resultado)
            else:
                st.warning("⚠️ Nenhum registro encontrado com id = 100")

        except Exception as erro:
            st.error(f"❌ Erro ao executar SQL: {erro}")
        finally:
            cursor.close()
            conexao.close()

   
# Interface Streamlit
#st.set_page_config(page_title="Conexão com Banco", page_icon="🗄️", layout="centered")
#st.title("🗄️ Conexão com SQL Server")

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

                
            else:
                st.info("Nenhuma tabela encontrada no banco.")
        except Exception as erro:
            st.error(f"Erro ao buscar dados: {erro}")
        finally:
            conexao.close()
    else:
        st.warning("Não foi possível estabelecer conexão.")