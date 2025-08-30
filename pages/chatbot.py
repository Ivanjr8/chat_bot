import streamlit as st
import google.generativeai as genai
import requests
from decoradores import acesso_restrito

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

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuração da Página
st.set_page_config(page_title="Chatbot", layout="wide")
# Titulo da página
st.title("🔄 Utilizar Chat Bot GEMINI")

# Obtendo KEYS SECRETS
gemini_key = st.secrets["GEMINI_API_KEY"]
SERP_API_KEY = st.secrets["SERP_API_KEYS"]
api_key = st.secrets["YOUTUBE_API_KEY"]


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
    
# Configurar Gemini
genai.configure(api_key=gemini_key) 
model = genai.GenerativeModel("gemini-1.5-flash")

# Funções de busca Links
def buscar_links_serpapi(consulta):
    url = "https://serpapi.com/search"
    params = {
        "q": consulta,
        "location": "Brazil",
        "hl": "pt",
        "gl": "br",
        "api_key": SERP_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    resultados = []
    for item in data.get("organic_results", []):
        titulo = item.get("title")
        link = item.get("link")
        if titulo and link:
            resultados.append((titulo, link))
    return resultados

# Funções de busca Vídeos
def buscar_videos_youtube(consulta):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": consulta,
        "type": "video",
        "maxResults": 5,
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    videos = []
    for item in data.get("items", []):
        titulo = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        link = f"https://www.youtube.com/watch?v={video_id}"
        videos.append((titulo, link))
    return videos

# Inicializar histórico
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Interface
# Botão para limpar chat
st.title("💬 Chatbot Inteligente com Links e Vídeos")
if st.button("🧹 Limpar conversa"):
    st.session_state.chat_history = []
    st.rerun()
# Caixa para digitar pergunta
user_input = st.text_input("Você:", key="input")

if user_input:
    # Adicionar pergunta ao histórico
    st.session_state.chat_history.append(("user", user_input))

    # Gerar resposta do Gemini
    #resposta = model.generate_content(user_input)
    resposta = model.generate_content(f"Responda como um chatbot amigável, em até 5 linhas:\n{user_input}")
    bot_reply = resposta.text.strip()
    st.session_state.chat_history.append(("bot", bot_reply))

    # Buscar links e vídeos
    links = buscar_links_serpapi(user_input)
    videos = buscar_videos_youtube(user_input)

    # Adicionar sugestões ao histórico
    if links:
        st.session_state.chat_history.append(("bot_links", "🔗 Aqui estão alguns links úteis:"))
        for titulo, url in links:
            st.session_state.chat_history.append(("bot_links", f"[{titulo}]({url})"))
    else:
        st.session_state.chat_history.append(("bot_links", "⚠️ Nenhum link encontrado."))

    if videos:
        st.session_state.chat_history.append(("bot_videos", "🎥 Vídeos relacionados:"))
        for titulo, url in videos:
            st.session_state.chat_history.append(("bot_videos", f"[{titulo}]({url})"))
    else:
        st.session_state.chat_history.append(("bot_videos", "⚠️ Nenhum vídeo encontrado."))

# Exibir histórico de conversa
for autor, mensagem in st.session_state.chat_history:
    if autor == "user":
        st.markdown(f"**👤 Você:** {mensagem}")
    else:
        st.markdown(f"**🤖 Bot:** {mensagem}")