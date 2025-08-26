import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Portal YOLO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização da barra lateral
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #1f2937;
            color: white;
        }
        [data-testid="stSidebar"] h2 {
            color: #10b981;
        }
        [data-testid="stSidebar"] .stButton button {
            background-color: #10b981;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Barra lateral personalizada
with st.sidebar:
    st.markdown("## 🧭 Navegação")
    if st.button("🤖 Ir para Chatbot"):
        st.switch_page("pages/chatbot.py")

    st.markdown("---")
    st.markdown("## ⚙️ Configurações")
    st.selectbox("Modo de exibição", ["Claro", "Escuro", "Automático"])
    st.slider("Sensibilidade do modelo", 0.0, 1.0, 0.5)

    st.markdown("---")
    st.markdown("### 📞 Suporte")
    st.write("Email: suporte@meuapp.com")

# Conteúdo principal
st.markdown(
    """
    <h1 style='text-align: center; color: #4B8BBE;'>🔮 Aplicativos de Detecção de Faces e Objetos</h1>
    """,
    unsafe_allow_html=True
)

with st.expander("ℹ️ Sobre este portal"):
    st.markdown(
        """
        Este é um hub de aplicativos de rede neural baseados em **YOLO (You Only Look Once)** para detecção de objetos e rostos em tempo real.

        - 📚 [Documentação oficial do Streamlit](https://docs.streamlit.io/)
        - 🐞 [Reportar falhas ou bugs](https://github.com/streamlit/streamlit/issues)
        """
    )

st.divider()
st.markdown("### 🧪 Escolha um aplicativo na barra lateral para começar.")