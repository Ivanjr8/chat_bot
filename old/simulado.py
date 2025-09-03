import streamlit as st
import pandas as pd
from pages.gemini_assistente import consultar_gemini
#from db_connection import DatabaseConnection
from db_connection1 import (
    buscar_escolas,
    buscar_alunos_por_escola,
    buscar_simulados_e_professores,
    consultar_simulado,
    salvar_resultado
)

# 🔐 Carregando as chaves do secrets.toml
GEMINI_API_KEY = st.secrets["api_keys"]["GEMINI_API_KEY"]
SERP_API_KEYS= st.secrets["api_keys"]["SERP_API_KEYS"]
YOUTUBE_API_KEY= st.secrets["api_keys"]["YOUTUBE_API_KEY"]

#GEMINI_API_KEY = "AIzaSyDz6PLA2Z1nT0-zuwZ-NehWFzU3pX7OMt0"
#SERP_API_KEYS = "19d8eb43b1f35459653abe2248c3788d0a2fd3274587b3d92c7bc137724b5b10"
#YOUTUBE_API_KEY = "AIzaSyDz6PLA2Z1nT0-zuwZ-NehWFzU3pX7OMt0"

# 🎯 Configurações da página
st.set_page_config(page_title="Simulado Educacional", layout="wide")
st.title("📘 Painel de Simulado Interativo")


# 🔐 Inicialização do estado
for var in ["aluno_id", "co_simulado", "consultado", "finalizado", "respostas_usuario"]:
    if var not in st.session_state:
        st.session_state[var] = None if var == "co_simulado" else False

# 🏫 Escolha da escola
busca_escola = st.text_input("Digite parte do nome da escola")
df_escolas = buscar_escolas()

if busca_escola:
    df_escolas_filtradas = df_escolas[
        df_escolas["NO_ESCOLA"].str.contains(busca_escola, case=False, na=False)
    ]

    if not df_escolas_filtradas.empty:
        escola_nome = st.selectbox("Selecione sua escola", df_escolas_filtradas["NO_ESCOLA"].tolist())
        escola_id = int(
            df_escolas_filtradas.loc[
                df_escolas_filtradas["NO_ESCOLA"] == escola_nome, "PK_ID_ESCOLA"
            ].iloc[0]
        )
        st.success(f"🏫 Escola selecionada: {escola_nome}")

        # 👨‍🎓 Autenticação do aluno
        df_alunos = buscar_alunos_por_escola(escola_id)
        alunos_opcoes = {
            f"{row['NO_NOME']} - Matrícula: {row['CO_MATRICULA']}": (
                row["PK_ID_ALUNO"], str(row["CO_MATRICULA"])
            )
            for _, row in df_alunos.iterrows()
        }

        aluno_selecionado = st.selectbox("Selecione seu nome e matrícula", list(alunos_opcoes.keys()))
        if aluno_selecionado:
            aluno_id, matricula_esperada = alunos_opcoes[aluno_selecionado]
            matricula_digitada = st.text_input("Digite sua matrícula para autenticação")

            if st.button("Autenticar"):
                if matricula_digitada.strip() == matricula_esperada.strip():
                    st.session_state.aluno_id = aluno_id
                    st.success(f"✅ Autenticado: {aluno_selecionado.split(' - ')[0]}")
                else:
                    st.error("❌ Matrícula incorreta.")
    else:
        st.warning("Nenhuma escola encontrada.")
else:
    st.info("Digite parte do nome da escola para buscar.")

# 🚦 Liberação do simulado após autenticação
if st.session_state.aluno_id:
    df_simulados = buscar_simulados_e_professores()
    professores = df_simulados["NO_NOME_PROFESSOR"].unique().tolist()
    professor_selecionado = st.selectbox("Selecione o nome do Professor", professores)

    simulados_do_professor = df_simulados[
        df_simulados["NO_NOME_PROFESSOR"] == professor_selecionado
    ]
    codigos_simulado = simulados_do_professor["CO_SIMULADO"].tolist()

    simulado_id = st.selectbox("Selecione o código do Simulado", codigos_simulado)
    st.session_state.co_simulado = simulado_id

    if st.button("Consultar Simulado"):
        st.session_state.consultado = True
        st.session_state.finalizado = False
  

    if st.session_state.consultado:
        with st.spinner("🔄 Consultando dados..."):
            df = consultar_simulado(simulado_id)

            if "CO_SIMULADO" not in df.columns:
                df["CO_SIMULADO"] = simulado_id

            if df.empty:
                st.warning("⚠️ Nenhum dado encontrado para esse código de simulado.")
            else:
                st.success(f"✅ {len(df)//4} Questões encontrados.")
                fil_descr = st.multiselect("Filtrar por Descritor", df.get("DESCRITOR", []).unique())
                if fil_descr:
                    df = df[df["DESCRITOR"].isin(fil_descr)]

                st.subheader("📝 Simulado Interativo")
                questoes = df.groupby("NUMERO DA QUESTÃO")
                respostas_usuario = {}

                for numero, grupo in questoes:
                    texto = grupo["PERGUNTA"].iloc[0]
                    descricao = grupo["DESCRIÇÃO DA PERGUNTA"].iloc[0]
                    alternativas = [
                        f"{alt}) {resp}"
                        for alt, resp in zip(grupo["NO_ALTERNATIVA"], grupo["NO_RESPOSTA"])
                    ]

                    st.markdown(f"*Texto: {descricao}*")
                    st.markdown(f"**Questão {numero}: {texto}**")
                    resposta = st.radio("Escolha uma alternativa:", alternativas, key=f"q{numero}")
                    codigo = resposta.split(")")[0].strip()

                    correta = grupo[grupo["NO_ALTERNATIVA"] == codigo]["CO_RESPOSTA_CORRETA"].iloc[0] if codigo in grupo["NO_ALTERNATIVA"].values else 0
                    resposta_correta = grupo[grupo["CO_RESPOSTA_CORRETA"] == 1]["NO_RESPOSTA"].iloc[0] if 1 in grupo["CO_RESPOSTA_CORRETA"].values else ""

                    respostas_usuario[numero] = {
                        "resposta": resposta,
                        "correta": correta,
                        "id_pergunta": grupo["CÓDIGO DA QUESTÃO"].iloc[0],
                        "disciplina": grupo["FK_CO_DISCIPLINA"].iloc[0],
                        "pergunta": texto,
                        "resposta_correta": resposta_correta
                    }

                if st.button("Finalizar Simulado") and not st.session_state.finalizado:
                    st.session_state.finalizado = True
                    st.session_state.respostas_usuario = respostas_usuario
                   
             

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

                    try:
                        for num, info in respostas_usuario.items():
                            resp_cod = info["resposta"].split(")")[0].strip()

                            # 🔍 Feedback por questão
                            if info["correta"] != 1:
                                st.warning(
                                    f"❌ Questão {num}: você respondeu '{info['resposta']}', "
                                    f"mas a resposta correta é '{info['resposta_correta']}'."
                                )

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

                            # 💾 Salvando no banco
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
                    except Exception as e:
                        st.error("❌ Erro ao salvar respostas.")
                        st.code(str(e), language="bash")
                        
                        
else:
    st.info("🔐 Você precisa se autenticar para acessar o simulado.")