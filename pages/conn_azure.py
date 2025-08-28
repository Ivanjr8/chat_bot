import streamlit as st
import pyodbc

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Estilização da barra lateral
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
           background: linear-gradient( #000000, #0000004c, #06080075);
           color: white;
           box-shadow: 0 0 10px rgba(0,0,0,0.5);
           padding: 20px;
           border-radius: 10px;
        }
       
        [data-testid="stSidebar"] {
           height: 100vh;
        overflow-y: auto;
}

        [data-testid="stSidebar"] h2 {
            color: #10b981;
        }
        [data-testid="stSidebar"] .stButton button {
           background-color: #0000004c;
           color: rgba(245, 245, 245, 0.849);
           text-align: left;
           padding-left: 12px;
           width: 240px;
           height: 40px;
           border: none;
           border-radius: 8px;
           font-size: 18px;
           font-weight: bold;
           box-shadow: 0 4px 6px rgba(0,0,0,0.1);
           cursor: pointer;
           transition: background-color 0.3s ease-in-out;
           display: flex;
           justify-content: flex-start;   /* Alinha conteúdo à esquerda */
           align-items: center;           /* Centraliza verticalmente */
           padding-left: 12px;            /* Espaço interno à esquerda */
           text-align: left;              /* Redundante, mas seguro */
        }
    </style>
""", unsafe_allow_html=True)

# 🧭 Barra lateral personalizada
with st.sidebar:
        if "usuario" in st.session_state and "perfil" in st.session_state:
            st.markdown(f"""
            👋 Olá, **{st.session_state.usuario}**  
            🔐 Perfil: **{st.session_state.perfil}**
            """)
        st.markdown("## 🧭 Navegação")
        if st.button("🎓   Chatbot", key="btn_chatbot"):
            st.switch_page("pages/chatbot.py")
        if st.button("🖥️   Gerar Simulado", key="btn_simulado"):
            st.switch_page("pages/Gerar_Simulado.py")
        if st.button("✅   Teste de Conexão", key="btn_azure"):
            st.switch_page("pages/conn_azure.py")
        if st.button("↩️   Retornar", key="btn_retornar"):
            st.switch_page("gemini.py")
        st.markdown("---")
        st.markdown("## ⚙️   Cadastro")
        if st.button("🗂️   Questões", key="btn_cadastrar"):
            st.switch_page("pages/Cadastrar_Questões.py")
        if st.button("🗂️   Respostas", key="btn_cadastrar_respostas"):
            st.switch_page("pages/Cadastrar_Respostas.py")
        if st.button("🗂️   Cadastrar Usuários", key="btn_cadastrar_usuarios"):
            st.switch_page("pages/Cadastrar_Usuarios.py")
            st.markdown("---")
        
        st.markdown("---")
        st.markdown("### 📞   Suporte")
        st.write("Email: suporte@meuapp.com")
        
        # Botão para sair
        if st.button("🚪 Sair"):
        # Remove dados de sessão
            for key in ["usuario", "perfil", "usuario_id"]:
                st.session_state.pop(key, None)
        # Redireciona para a página inicial (gemini.py)
                st.switch_page("gemini.py")
            # Reinicia a aplicação
                st.rerun()
    
# Função de conexão
def conectar_banco():
    try:
        conexao = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=srvappmba.database.windows.net;"
            "DATABASE=myFreeDB;"
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

                
            else:
                st.info("Nenhuma tabela encontrada no banco.")
        except Exception as erro:
            st.error(f"Erro ao buscar dados: {erro}")
        finally:
            conexao.close()
    else:
        st.warning("Não foi possível estabelecer conexão.")