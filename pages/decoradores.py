import streamlit as st
from functools import wraps
from db_connection import DatabaseConnection


def acesso_restrito(id_modulo):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verifica se o perfil está na sessão
            if "perfil" not in st.session_state:
                st.warning("⚠️ Você precisa estar logado.")
                st.stop()

            perfil = st.session_state["perfil"].lower()

            # Conecta ao banco
            db = DatabaseConnection()
            db.connect()
            cursor = db.conn.cursor()

            # Verifica se o perfil tem acesso ao módulo
            cursor.execute("""
                SELECT 1 FROM TB_012_ACESSOS
                WHERE LOWER(perfil) = ? AND id_modulo = ?
            """, (perfil, id_modulo))

            if not cursor.fetchone():
                st.error("🚫 Acesso negado. Você não tem permissão para acessar esta página.")
                st.stop()

            return func(*args, **kwargs)
        return wrapper
    return decorador

