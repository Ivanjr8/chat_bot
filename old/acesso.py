import streamlit as st
from db_connection import DatabaseConnection

# 🔧 Estilo personalizado
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# 🔌 Conexão com o banco
db = DatabaseConnection()
db.connect()

st.title("🔐 Gerenciar Matriz de Acesso")

# 🔍 Selecionar usuário
usuarios = db.get_usuarios()
usuario_nomes = [u["usuario"] for u in usuarios]
usuario_selecionado = st.selectbox("👤 Selecione um usuário", usuario_nomes)

usuario_id = next(u["id"] for u in usuarios if u["usuario"] == usuario_selecionado)

# 📦 Carregar módulos e acessos
modulos = db.get_modulos()
acessos_atuais = db.get_acessos_usuario(usuario_id)

st.subheader("🧭 Permissões por módulo")

# 🔁 Interface de checkboxes
for modulo in modulos:
    permitido = modulo["id"] in acessos_atuais
    novo_valor = st.checkbox(modulo["nome"], value=permitido, key=f"mod_{modulo['id']}")
    
    if novo_valor != permitido:
        db.set_acesso(usuario_id, modulo["id"], int(novo_valor))
        st.toast(f"✅ Permissão para '{modulo['nome']}' atualizada.")
        st.rerun()

db.close()