import streamlit as st
import google.generativeai as genai
import requests

# 🔐 Carregando as chaves do secrets.toml
#GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
#SERP_API_KEYS = st.secrets["SERP_API_KEYS"]
#YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

GEMINI_API_KEY = st.secrets["api_keys"]["GEMINI_API_KEY"]
SERP_API_KEYS= st.secrets["api_keys"]["SERP_API_KEYS"]
YOUTUBE_API_KEY= st.secrets["api_keys"]["YOUTUBE_API_KEY"]

# ⚙️ Configurando o modelo Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 🔎 Função para buscar links via SerpApi
def buscar_links_serpapi(consulta):
    url = "https://serpapi.com/search"
    params = {
        "q": consulta,
        "location": "Brazil",
        "hl": "pt",
        "gl": "br",
        "api_key": SERP_API_KEYS
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

# 🎥 Função para buscar vídeos no YouTube
def buscar_videos_youtube(consulta):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": consulta,
        "type": "video",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
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

# 🧠 Função para consultar Gemini e gerar explicação + sugestões
def consultar_gemini(pergunta, resposta_errada, descricao):
    prompt = (
        f"Explique de forma clara e objetiva (até 5 linhas) a seguinte pergunta de simulado:\n"
        f"Texto de apoio: {descricao}\n"
        f"Pergunta: {pergunta}\n"
        f"Resposta incorreta escolhida: {resposta_errada}\n"
        f"Ajude o aluno a entender o erro e aprender o conteúdo."
    )
    try:
        resposta = model.generate_content(prompt)
        explicacao = resposta.text.strip()
    except Exception as e:
        explicacao = f"Erro ao gerar explicação: {e}"

    # Buscar links de estudo
    try:
        links_estudo = buscar_links_serpapi(pergunta)
    except Exception:
        links_estudo = []

    # Buscar vídeos educativos
    try:
        videos = buscar_videos_youtube(pergunta)
    except Exception:
        videos = []

    return {
        "explicacao": explicacao,
        "links_estudo": links_estudo,
        "videos": videos

    }


# # 🧠 Função principal para gerar explicação com Gemini
# def consultar_gemini(pergunta, resposta_errada):
#     prompt = f"""
#     A pergunta é: "{pergunta}"
#     O aluno respondeu incorretamente: "{resposta_errada}"

#     1. Identifique o descritor associado a essa pergunta.
#     2. Explique o conteúdo correto de forma simples e clara, como se estivesse ensinando a um estudante do ensino fundamental.
#     3. Destaque o erro comum cometido e por que a resposta correta é mais adequada.
#     4. Sugira uma dica prática para o aluno lembrar desse conteúdo no futuro.
#     """

#     try:
#         resposta = model.generate_content(prompt)
#         explicacao = resposta.text.strip()

#         # Busca de links e vídeos complementares
#         links = buscar_links_serpapi(pergunta)
#         videos = buscar_videos_youtube(pergunta)

#         return {
#             "explicacao": explicacao,
#             "links_estudo": links[:3],  # aumentei para 3 links
#             "videos": videos[:3]        # aumentei para 3 vídeos
#         }

#     except Exception as e:
#         return {
#             "explicacao": f"⚠️ Erro ao gerar explicação: {str(e)}",
#             "links_estudo": [],
#             "videos": []
#         }