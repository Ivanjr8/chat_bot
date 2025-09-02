import streamlit as st
from decoradores import acesso_restrito
import pandas as pd
import math
from pages.gemini_assistente import consultar_gemini
from db_connection import DatabaseConnection

db = DatabaseConnection()
df = db.buscar_escolas()

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuração da Página
st.set_page_config(page_title="Gerar Simulado", layout="wide")
# # Titulo da página
st.title(" Gerar Simulado - Página em Construção")
# # Adicionar Imagem 
# st.image("em_construcao.jpg", caption="Estamos trabalhando nisso!", width=600)

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

# Conexão com o banco
db = DatabaseConnection()
db.connect()

if not db.conn:
    st.error("❌ Falha na conexão com o banco.")
    st.stop()
   
        
# Conteúdo após login
# 🔧 Estilo personalizado
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil

# 🔍 Função para buscar acessos permitidos
def buscar_acessos_permitidos(perfil):
    try:
        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT id_modulo FROM TB_012_ACESSOS WHERE LOWER(perfil) = ?",
            (perfil,)
        )
        
        # 🔽 Aqui entra sua ordenação personalizada
        ordem_personalizada = [1, 2, 3, 4, 5, 6, 7, 9, 97, 98, 99]
        modulos_permitidos = [row[0] for row in cursor.fetchall()]
        modulos_ordenados = [mod for mod in ordem_personalizada if mod in modulos_permitidos]
        
        return modulos_ordenados

    except Exception as e:
        st.error(f"Erro ao buscar acessos: {e}")
        return []

# 🗺️ Mapeamento de módulos para botões e páginas
botoes_paginas = {
    1: {"label": "🎓   Chatbot", "page": "pages/chatbot.py", "key": "btn_chatbot"},
    2: {"label": "🖥️   Gerar Simulado", "page": "pages/Gerar_Simulado.py", "key": "btn_simulado"},
    
}
botoes_cadastro = {
    3: {"label": "🗂️   Questões", "page": "pages/Cadastrar_Questões.py", "key": "btn_cadastrar"},
    4: {"label": "🗂️   Respostas", "page": "pages/Cadastrar_Respostas.py", "key": "btn_cadastrar_respostas"},
    5: {"label": "🗂️   Escolas", "page": "pages/Cadastrar_Escolas.py", "key": "btn_escolas"},
    9: {"label": "🗂️   Usuários", "page": "pages/Cadastrar_Usuarios.py", "key": "btn_ Cadastrar_Usuarios"},
}
botoes_admin = {
    7: {"label": "✅   Teste de  Conexão", "page": "pages/conn_azure.py", "key": "conn_azure.py"},
    6: {"label": "🗂️   matriz", "page": "pages/matriz.py", "key": "btn_matriz"},
        
}
botoes_retornar = {
    99: {"label": "↩️   Retornar", "page": "gemini.py", "key": "btn_retornar"},  # acesso universal
}

botoes_link_aluno = {
    98: {
        "label": "📊   Painel do Aluno",
        "page": "https://app.powerbi.com/view?r=eyJrIjoiN2M2NWM1N2QtYWQ3My00NjM1LWFiMWQtMjg0YTIxMzMxNjNhIiwidCI6IjRhMjJmMTE2LTUxY2UtNGZlMy1hZWFhLTljNDYxNDNkMDg4YiJ9",
        "key": "btn_powerbi"
    }
}

botoes_link_professor = {
    97: {
        "label": "📊   Painel Professor",
        "page": "https://app.powerbi.com/view?r=eyJrIjoiYTAzMWJhZGYtMzI1ZS00MzkwLThiOGYtOGEwNWU4ZDUzMGVjIiwidCI6IjRhMjJmMTE2LTUxY2UtNGZlMy1hZWFhLTljNDYxNDNkMDg4YiJ9",
        "key": "btn_powerbi"
    }
}
        
# 🔧 Conteúdo após login
if "usuario" in st.session_state and "perfil" in st.session_state:
    perfil = st.session_state.perfil
    usuario = st.session_state.usuario

    modulos_permitidos = buscar_acessos_permitidos(perfil)
    
    # 👇 Adicione aqui para depurar
    #st.write("Modulos permitidos:", modulos_permitidos)
    #st.write("IDs disponíveis em botoes_cadastro:", list(botoes_cadastro.keys()))

    with st.sidebar:
        st.markdown(f"""
        👋 Olá, **{usuario}**  
        🔐 Perfil: **{perfil}**
        """)
        st.markdown("## 🧭 Navegação")

        for mod_id in modulos_permitidos:
            if mod_id in botoes_paginas:
                btn = botoes_paginas[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_navegacao"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])

        st.markdown("## ⚙️   Cadastro")

        for mod_id in modulos_permitidos:
            if mod_id in botoes_cadastro:
                btn = botoes_cadastro[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])

        st.markdown("## ⚙️   Administrativo")
        for mod_id in modulos_permitidos:
            if mod_id in botoes_admin:
                btn = botoes_admin[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])

        for mod_id in modulos_permitidos + [99]:
            if mod_id in botoes_retornar:
                btn = botoes_retornar[mod_id]
                chave_unica = f"{btn['key']}_{mod_id}_cadastro"
                st.session_state.chat_history = []
                st.session_state.aluno_id = None
                if st.button(btn["label"], key=chave_unica):
                    st.switch_page(btn["page"])
                    
                    
                    
        
        if perfil in ['Aluno', 'Administrador']:
            for mod_id in botoes_link_aluno:
                btn = botoes_link_aluno[mod_id]
                st.markdown("""
                <style>
                    .custom-btn {
                        background-color: #0000004c;
                        color: rgba(245, 245, 245, 0.849) !important;
                        text-align: left;
                        padding-left: 12px;
                        width: 240px;
                        height: 40px;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: background-color 0.3s ease-in-out;
                        display: flex;
                        justify-content: flex-start;
                        align-items: center;
                        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
                        transform: scale(1.02);
                        text-decoration: none !important;
                    }

                    .custom-btn:hover {
                        background-color: #10b981;
                        color: white;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <a href="{btn['page']}" target="_blank" class="custom-btn">
                    {btn['label']}
                </a>
            """, unsafe_allow_html=True)
         # 🎓 Botões exclusivos para Alunos
        if perfil != "Aluno":
            for mod_id in botoes_link_professor:
                btn = botoes_link_professor[mod_id]
                st.markdown("""
                <style>
                    .custom-btn {
                        background-color: #0000004c;
                        color: rgba(245, 245, 245, 0.849) !important;
                        text-align: left;
                        padding-left: 12px;
                        width: 240px;
                        height: 40px;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: background-color 0.3s ease-in-out;
                        display: flex;
                        justify-content: flex-start;
                        align-items: center;
                        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
                        transform: scale(1.02);
                        text-decoration: none !important;
                    }

                    .custom-btn:hover {
                        background-color: #10b981;
                        color: white;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <a href="{btn['page']}" target="_blank" class="custom-btn">
                    {btn['label']}
                </a>
            """, unsafe_allow_html=True)

        st.markdown("### 📞   Suporte")
        st.write("Email: suporte@meuapp.com")
        
         # 🚪 Botão para sair
        if st.button("🚪 Sair"):
            for key in ["usuario", "perfil", "usuario_id"]:
                st.session_state.pop(key, None)
            st.switch_page("gemini.py")
            st.rerun()  
# simulado #############################################################################

# 🔐 Inicialização do estado da sessão
for var in ["aluno_id", "co_simulado", "consultado", "finalizado", "respostas_usuario"]:
    if var not in st.session_state:
        if var == "co_simulado":
            st.session_state[var] = None
        elif var == "respostas_usuario":
            st.session_state[var] = {}
        else:
            st.session_state[var] = False

# 🏫 Escolha da escola
busca_escola1 = st.text_input("Digite parte do nome da escola")
db = DatabaseConnection()
df_escolas = db.buscar_escolas1(busca_escola1)

if busca_escola1:
    # Filtra escolas pelo nome digitado
    df_escolas_filtradas = df_escolas[
        df_escolas["NO_ESCOLA"].str.contains(busca_escola1, case=False, na=False)
    ]

    if not df_escolas_filtradas.empty:
        escola_nome = st.selectbox("Selecione sua escola", df_escolas_filtradas["NO_ESCOLA"].tolist())
        escola_id = int(df_escolas_filtradas.loc[
            df_escolas_filtradas["NO_ESCOLA"] == escola_nome, "PK_ID_ESCOLA"
        ].iloc[0])
        st.success(f"🏫 Escola selecionada: {escola_nome}")

        # 👨‍🎓 Autenticação do aluno
        df_alunos = db.buscar_alunos_por_escola(escola_id)
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
#     else:
#         st.warning("Nenhuma escola encontrada.")
# else:
#     st.info("Digite parte do nome da escola para buscar.")

# 🚦 Liberação do simulado após autenticação
if st.session_state.aluno_id:
    df_simulados = db.buscar_simulados_e_professores()
    professores = df_simulados["NO_NOME_PROFESSOR"].unique().tolist()
    professor_selecionado = st.selectbox("Selecione o nome do Professor", professores)

    simulados_do_professor = df_simulados[df_simulados["NO_NOME_PROFESSOR"] == professor_selecionado]
    codigos_simulado = simulados_do_professor["CO_SIMULADO"].tolist()

    simulado_id = st.selectbox("Selecione o código do Simulado", codigos_simulado)
    st.session_state.co_simulado = simulado_id

    if st.button("Consultar Simulado"):
        st.session_state.consultado = True
        st.session_state.finalizado = False

    if st.session_state.consultado:
        with st.spinner("🔄 Consultando dados..."):
            df = db.consultar_simulado(simulado_id)

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
                        f"{alt}) {resp}" for alt, resp in zip(grupo["NO_ALTERNATIVA"], grupo["NO_RESPOSTA"])
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
                        "descricao": descricao,
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

                    # 🔁 Loop para salvar cada resposta
                                         
                    for num, info in respostas_usuario.items():
                        resp_cod = info["resposta"].split(")")[0].strip()

                        if info["correta"] != 1:
                            st.warning(f"❌ Questão {num}: você respondeu '{info['resposta']}', mas a resposta correta é '{info['resposta_correta']}'.")

                            resultado_ia = consultar_gemini(
                                pergunta=info["pergunta"],
                                resposta_errada=info["resposta"],
                                descricao=info["descricao"]
                            )
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

                        try:
                            sucesso = db.salvar_resultado_resposta(
                                pergunta_id=int(info["id_pergunta"]),
                                resposta_aluno=str(resp_cod),
                                disciplina_id=int(info["disciplina"]),
                                correta=int(info["correta"]),
                                co_simulado=int(st.session_state.co_simulado),
                                aluno_id=int(st.session_state.aluno_id),
                                co_tentativa=int(1)
                            )
                            if sucesso:
                                st.info(f"💾 Resposta da pergunta {info['id_pergunta']} salva com sucesso.")
                            else:
                                st.warning(f"⚠️ Falha ao salvar resposta da pergunta {info['id_pergunta']}.")
                        except Exception as e:
                            st.error("❌ Erro ao salvar respostas.")
                            st.code(str(e), language="bash")

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("### Finalizou o simulado?")
                if st.button("🔁 Reiniciar"):
                    st.session_state.aluno_id = None
                    st.rerun()
                    
                # 🧹 Botão para limpar conversa
                
                st.title("💬 Chatbot Inteligente com Links e Vídeos")
                if st.button("🧹 Limpar conversa"):
                    st.session_state.chat_history = []
                    st.session_state.aluno_id = None
                    st.rerun()
                                            
    db.close()
        
        

