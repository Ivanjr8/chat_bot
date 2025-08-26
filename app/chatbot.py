import streamlit as st
import google.generativeai as genai
import requests

# Obtendo KEYS SECRETS
gemini_key = st.secrets["GEMINI_API_KEY"]
SERP_API_KEY = st.secrets["SERP_API_KEYS"]
api_key = st.secrets["YOUTUBE_API_KEY"]



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