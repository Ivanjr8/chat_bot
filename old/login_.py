import streamlit as st
from db_connection import DatabaseConnection

# 🔧 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Configuração da página
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")


st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🎒 Aplicação para Avaliação de Alunos</h1>", unsafe_allow_html=True)

with st.expander("ℹ️ Sobre este portal"):
        st.markdown("""
            Este é um aplicativo que utiliza IA com consultas ao chatbot (GEMINI) para gerar simulados de acordo com descritores,
            apresentando sugestões de conteúdo para estudo das questões respondidas de forma errada.

            - 📚 [Documentação oficial do Streamlit](https://docs.streamlit.io/)
            - 🐞 [Reportar falhas ou bugs](https://github.com/streamlit/streamlit/issues)
        """)

st.divider()
st.markdown("### 🧪 Bem-vindo ao APP Simulado assistido por IA")