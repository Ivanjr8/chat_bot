import streamlit as st
from db_connection import DatabaseConnection
import math
import pandas as pd

# 🌈 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ⚙️ Configuração da página
st.set_page_config(page_title="Gerar Simulado", layout="wide")

# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()

# 🔍 Campo de busca
nome_escola1 = st.text_input("🔍 Digite parte do nome da escola:")

# 🔄 Carrega todas as escolas
todas_escolas = db.get_escolas("")  # sem filtro

# 🔎 Filtra escolas com base no texto digitado
escolas_filtradas = []
if nome_escola1:
    escolas_filtradas = [
        e for e in todas_escolas
        if nome_escola1.lower() in e['NO_ESCOLA'].lower()
    ]

# 🏫 Se houver uma única escola, exibe diretamente
if len(escolas_filtradas) == 1:
    escola = escolas_filtradas[0]
    escola_nome = escola['NO_ESCOLA']
    escola_id = escola['PK_ID_ESCOLA']

    #st.success(f"🏫 Escola encontrada: **{escola_nome}**")

    # Após definir escola_nome e escola_id
    col_escola1, col_escola2 = st.columns([3, 1])
    with col_escola1:
        st.success(f"🏫 Escola encontrada: **{escola_nome}**")
    with col_escola2:
        escola_ativa = st.toggle("Ativa", key=f"toggle_escola_{escola_id}")

    
    professores = db.professores_por_escola(escola_id)

    if professores:
        st.markdown(f"### 👨‍🏫 Professores da escola **{escola_nome}**")

        # Lista para armazenar IDs dos professores ativos
        ids_ativos = []

        for prof in professores:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 {prof['NO_NOME_PROFESSOR']}")
            with col2:
                status = st.toggle("Ativo", key=f"toggle_{prof['PK_CO_PROFESSOR']}")
                if status:
                    ids_ativos.append(prof['PK_CO_PROFESSOR'])

        st.caption(f"Total de professores: {len(professores)}")
        st.markdown("🟢 **IDs dos professores ativos:**")
        st.write(ids_ativos)

    else:
        st.warning("Nenhum professor encontrado para esta escola.")

# 📋 Se houver múltiplas escolas, permite seleção
elif len(escolas_filtradas) > 1:
    escola_opcoes = {e['NO_ESCOLA']: e['PK_ID_ESCOLA'] for e in escolas_filtradas}
    escola_nome = st.selectbox("Selecione a escola:", list(escola_opcoes.keys()))
    escola_id = escola_opcoes[escola_nome]

    # Exibe nome da escola e botão de ativação lado a lado
    col_escola1, col_escola2 = st.columns([3, 1])
    with col_escola1:
        st.success(f"🏫 Escola selecionada: **{escola_nome}**")
    with col_escola2:
        escola_ativa = st.toggle("Ativa", key=f"toggle_escola_{escola_id}")

    professores = db.professores_por_escola(escola_id)

    if professores:
        st.markdown(f"### 👨‍🏫 Professores da escola **{escola_nome}**")

        ids_ativos = []

        for prof in professores:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 {prof['NO_NOME_PROFESSOR']}")
            with col2:
                status = st.toggle("Ativo", key=f"toggle_{prof['PK_CO_PROFESSOR']}")
                if status:
                    ids_ativos.append(prof['PK_CO_PROFESSOR'])

        st.caption(f"Total de professores: {len(professores)}")
        st.markdown("🟢 **IDs dos professores ativos:**")
        st.write(ids_ativos)

    else:
        st.warning("Nenhum professor encontrado para esta escola.")









# # 👨‍🏫 Escolha do professor
#     db = DatabaseConnection()
#     db.connect()
# db_professores = professores_por_escola(escola_id)
# prof_opcoes = {p['NO_NOME_PROFESSOR']: p['PK_CO_PROFESSOR'] for p in db_professores}
# prof_nome = st.selectbox("👨‍🏫 Escolha o professor", list(prof_opcoes.keys()))
# prof_id = prof_opcoes[prof_nome]

# # 📚 Escolha da disciplina
# df_disciplinas = disciplinas()
# disc_opcoes = {d['NO_DISCIPLINA'].strip(): d['PK_CO_DISCIPLINA'] for d in df_disciplinas}
# disc_nome = st.selectbox("📚 Escolha a disciplina", list(disc_opcoes.keys()))
# disc_id = disc_opcoes[disc_nome]

# # 🧠 Escolha do descritor
# df_descritores = descritores()
# descritor_opcoes = {
#     d['no_descritor'].strip(): d['PK_ID_DESCRITOR']
#     for d in descritores if d['FK_CO_DISCIPLINA'] == disc_id
# }
# descritor_nome = st.selectbox("🧠 Escolha o descritor", list(descritor_opcoes.keys()))
# descritor_id = descritor_opcoes[descritor_nome]

# # 📝 Seleção de perguntas
# df_perguntas = perguntas()
# perguntas_filtradas = [
#     p for p in perguntas
#     if p['FK_CO_DISCIPLINA'] == disc_id and p['FK_CO_DESCRITOR'] == descritor_id
# ]

# st.markdown("### 📝 Perguntas disponíveis")
# selecionadas = []
# for pergunta in perguntas_filtradas:
#     texto = f"{pergunta['NO_PERGUNTA'].strip()} — {pergunta['DE_PERGUNTA'].strip()}"
#     if st.checkbox(texto, key=f"pergunta_{pergunta['PK_CO_PERGUNTA']}"):
#         selecionadas.append(pergunta)

# # 🔢 Código do simulado
# co_simulado = st.number_input("🔢 Código do Simulado", min_value=1, value=1)

# # ✅ Botão para adicionar ao simulado
# if st.button("✅ Adicionar ao Simulado"):
#     if not selecionadas:
#         st.warning("⚠️ Selecione ao menos uma pergunta.")
#     else:
#         for pergunta in selecionadas:
#              insert_simulado(
#                 co_simulado=co_simulado,
#                 fk_escola=escola_id,
#                 fk_professor=prof_id,
#                 fk_pergunta=pergunta['PK_CO_PERGUNTA'],
#                 fk_disciplina=disc_id,
#                 fk_descritor=descritor_id
#             )
#         st.success(f"{len(selecionadas)} pergunta(s) adicionada(s) ao simulado!")

# close()