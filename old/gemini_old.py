#import google.generativeai as genai

#genai.configure(api_key="AIzaSyDz6PLA2Z1nT0-zuwZ-NehWFzU3pX7OMt0")

#model = genai.GenerativeModel("gemini-1.5-flash")

#response = model.generate_content("Explique o que é Snowflake em 3 frases.")
#print(response.text)

#for m in genai.list_models():
#    print(m.name)
#

import streamlit as st
import google.generativeai as genai
import os

# Configurar chave da API
genai.configure(api_key="AIzaSyDz6PLA2Z1nT0-zuwZ-NehWFzU3pX7OMt0")

# Inicializar modelo
model = genai.GenerativeModel("gemini-1.5-flash")

# Interface do chatbot
st.title("🤖 Chatbot Gemini - Respostas Curtas")
st.caption("Respostas limitadas a 2 linhas para cada pergunta.")

# Entrada do usuário
user_input = st.text_input("Digite sua pergunta:")

# Lógica de resposta
if user_input:
    prompt = f"Responda à pergunta abaixo em no máximo 2 linhas:\n{user_input}"
    response = model.generate_content(prompt)
    st.markdown(f"**Resposta:** {response.text}")