import streamlit as st
import pandas as pd
from decoradores import acesso_restrito
from pages.gemini_assistente import consultar_gemini
from db_connection import DatabaseConnection
import math

db = DatabaseConnection()
df = db.buscar_escolas()

# 🔌 Instância da conexão
db = DatabaseConnection()
df_simulados = db.buscar_simulados_e_professores()


# 🏫 Escolha da escola
busca_escola1 = st.text_input("Digite parte do nome da escola")

if busca_escola1:
    db = DatabaseConnection()
    df_escolas = db.buscar_escolas1(busca_escola1)

    if df_escolas.empty:
        st.warning("Nenhuma escola encontrada.")
    else:
        # Cria um dicionário: "Nome da Escola (ID: 123)" → ID
        escolas_opcoes = {
            f"{row['NO_ESCOLA']} (ID: {row['PK_ID_ESCOLA']})": row["PK_ID_ESCOLA"]
            for _, row in df_escolas.iterrows()
        }

        # Selectbox com nome + ID
        escola_selecionada = st.selectbox("Selecione sua escola", list(escolas_opcoes.keys()))

        # Recupera o ID diretamente
        escola_id = escolas_opcoes[escola_selecionada]

        # Exibe confirmação
        st.markdown(f"🏫 **Escola selecionada:** `{escola_selecionada}`")
        st.markdown(f"🔑 **ID da escola:** `{escola_id}`")

# inicia outro trecho

        df_alunos = db.buscar_alunos_por_escola(escola_id)
        #st.table(df_alunos)

        
        if df_alunos.empty:
            st.warning("Nenhum aluno encontrado para esta escola.")
        else:
            alunos_opcoes = {
                f"{row['NO_NOME']} - Matrícula: {row['CO_MATRICULA']}": (
                    row["PK_ID_ALUNO"], str(row["CO_MATRICULA"])
                )
                for _, row in df_alunos.iterrows()
            }

            aluno_selecionado = st.selectbox("Selecione seu nome e matrícula", list(alunos_opcoes.keys()))
            aluno_id, matricula_esperada = alunos_opcoes[aluno_selecionado]
            matricula_digitada = st.text_input("Digite sua matrícula para autenticação")

            if st.button("Autenticar"):
                if not matricula_digitada:
                    st.warning("Digite sua matrícula para autenticação.")
                elif matricula_digitada.strip() == matricula_esperada.strip():
                    st.session_state.aluno_id = aluno_id
                    st.success(f"✅ Autenticado: {aluno_selecionado.split(' - ')[0]}")
                else:
                    st.error("❌ Matrícula incorreta.")
else:
    st.info("Digite parte do nome da escola para buscar.")


# 🔐 Inicialização do estado
for var in ["aluno_id", "co_simulado", "consultado", "finalizado", "respostas_usuario"]:
    if var not in st.session_state:
        st.session_state[var] = None if var == "co_simulado" else False
        
# Verifica se o usuário está autenticado
if "aluno_id" in st.session_state:
    # 🔓 Usuário autenticado — pode acessar o simulado

    import streamlit as st
import pandas as pd

def consultar_simulado(simulado_id):
    db = DatabaseConnection()
    df = db.consultar_simulado(simulado_id)
    if "CO_SIMULADO" not in df.columns:
        df["CO_SIMULADO"] = simulado_id
    return df

def validar_colunas(df, colunas):
    faltando = [col for col in colunas if col not in df.columns]
    if faltando:
        st.error(f"❌ Colunas ausentes: {', '.join(faltando)}")
        st.stop()

def renderizar_questoes(df):
    respostas_usuario = {}
    questoes = df.groupby("NUMERO DA QUESTÃO")
    for numero, grupo in questoes:
        texto = grupo["PERGUNTA"].iloc[0]
        descricao = grupo["DESCRIÇÃO DA PERGUNTA"].iloc[0]
        alternativas = [f"{alt}) {resp}" for alt, resp in zip(grupo["NO_ALTERNATIVA"], grupo["NO_RESPOSTA"])]

        st.markdown(f"*Texto: {descricao}*")
        st.markdown(f"**Questão {numero}: {texto}**")

        if alternativas:
            resposta = st.radio("Escolha uma alternativa:", alternativas, key=f"q{numero}")
            codigo = resposta.split(")")[0].strip()
            correta = grupo[grupo["NO_ALTERNATIVA"] == codigo]["CO_RESPOSTA_CORRETA"].iloc[0] if codigo in grupo["NO_ALTERNATIVA"].values else 0
            resposta_correta = grupo[grupo["CO_RESPOSTA_CORRETA"] == 1]["NO_RESPOSTA"].iloc[0] if 1 in grupo["CO_RESPOSTA_CORRETA"].values else ""
        else:
            st.warning(f"⚠️ Questão {numero} não possui alternativas.")
            resposta, correta, resposta_correta = "", 0, ""

        respostas_usuario[numero] = {
            "resposta": resposta,
            "correta": correta,
            "id_pergunta": grupo["CÓDIGO DA QUESTÃO"].iloc[0],
            "disciplina": grupo["FK_CO_DISCIPLINA"].iloc[0],
            "pergunta": texto,
            "descricao": descricao,
            "resposta_correta": resposta_correta
        }
    return respostas_usuario

def finalizar_simulado(respostas_usuario):
    total = len(respostas_usuario)
    acertos = sum(r["correta"] for r in respostas_usuario.values())
    st.success(f"🎉 Você acertou {acertos} de {total} questões ({acertos/total*100:.1f}%)")

    resumo = pd.DataFrame([
        {
            "Questão": num,
            "Pergunta": info["pergunta"],
            "Resposta do Usuário": info["resposta"],
            "Resposta Correta": info["resposta_correta"] if info["correta"] != 1 else "",
            "Resultado": "✅ Correta" if info["correta"] == 1 else "❌ Incorreta"
        }
        for num, info in respostas_usuario.items()
    ])
    st.dataframe(resumo, use_container_width=True)

    for num, info in respostas_usuario.items():
        resp_cod = info["resposta"].split(")")[0].strip()
        if info["correta"] != 1:
            st.warning(f"❌ Questão {num}: você respondeu '{info['resposta']}', mas a resposta correta é '{info['resposta_correta']}'.")
            resultado_ia = consultar_gemini(info["pergunta"], info["resposta"])
            st.markdown("#### 💡 Explicação da IA")
            st.info(resultado_ia["explicacao"])
            st.markdown("#### 📚 Links para estudo")
            for titulo, link in resultado_ia["links_estudo"]:
                st.markdown(f"- [{titulo}]({link})")
            st.markdown("#### 🎥 Vídeos sugeridos")
            for titulo, link in resultado_ia["videos"]:
                st.markdown(f"- [{titulo}]({link})")
        else:
            st.success(f"✅ Questão {num}: resposta correta!")

        sucesso = salvar_resultado(
            pergunta_id=info["id_pergunta"],
            resposta_aluno=resp_cod,
            disciplina_id=info["disciplina"],
            correta=info["correta"],
            co_simulado=st.session_state.co_simulado,
            aluno_id=st.session_state.aluno_id
        )
        if sucesso:
            st.info(f"💾 Resposta da pergunta {info['id_pergunta']} salva com sucesso.")
        else:
            st.warning(f"⚠️ Falha ao salvar resposta da pergunta {info['id_pergunta']}.")

# 🔐 Verifica se o usuário está autenticado
if "aluno_id" in st.session_state:
    if not df_simulados.empty:
        professores = df_simulados["NO_NOME_PROFESSOR"].dropna().unique().tolist()
        professor_selecionado = st.selectbox("Selecione o nome do Professor", professores)
        simulados_do_professor = df_simulados[df_simulados["NO_NOME_PROFESSOR"] == professor_selecionado]
        codigos_simulado = simulados_do_professor["CO_SIMULADO"].dropna().tolist()

        if codigos_simulado:
            simulado_id = st.selectbox("Selecione o código do Simulado", codigos_simulado)
            st.session_state.co_simulado = simulado_id

            if st.button("Consultar Simulado"):
                st.session_state.consultado = True
                st.session_state.finalizado = False

            if st.session_state.consultado:
                with st.spinner("🔄 Consultando dados..."):
                    df = consultar_simulado(simulado_id)

                    if df.empty:
                        st.warning("⚠️ Nenhum dado encontrado para esse código de simulado.")
                    else:
                        st.success(f"✅ {len(df)//4} Questões encontrados.")
                        descritores = df["DESCRITOR"].dropna().unique().tolist() if "DESCRITOR" in df.columns else []
                        fil_descr = st.multiselect("Filtrar por Descritor", descritores)
                        if fil_descr:
                            df = df[df["DESCRITOR"].isin(fil_descr)]

                        st.subheader("📝 Simulado Interativo")
                        validar_colunas(df, [
                            "NUMERO DA QUESTÃO", "PERGUNTA", "DESCRIÇÃO DA PERGUNTA",
                            "NO_ALTERNATIVA", "NO_RESPOSTA", "CO_RESPOSTA_CORRETA"
                        ])

                        respostas_usuario = renderizar_questoes(df)

                        if st.button("Finalizar Simulado") and not st.session_state.finalizado:
                            st.session_state.finalizado = True
                            st.session_state.respostas_usuario = respostas_usuario
                            finalizar_simulado(respostas_usuario)

                        st.title("💬 Chatbot Inteligente com Links e Vídeos")
                        if st.button("🧹 Limpar conversa"):
                            st.session_state.chat_history = []
                            st.rerun()
        else:
            st.warning("Este professor não possui simulados disponíveis.")
    else:
        st.warning("Nenhum simulado disponível no momento.")
else:
    st.info("🔐 Você precisa se autenticar para acessar o simulado.")