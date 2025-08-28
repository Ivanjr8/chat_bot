import streamlit as st
import google.generativeai as genai
import requests

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Obtendo KEYS SECRETS
gemini_key = st.secrets["GEMINI_API_KEY"]
SERP_API_KEY = st.secrets["SERP_API_KEYS"]
api_key = st.secrets["YOUTUBE_API_KEY"]


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