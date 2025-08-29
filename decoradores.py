# decoradores.py
import streamlit as st
from functools import wraps
from db_connection import DatabaseConnection

def acesso_restrito(id_modulo):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "perfil" not in st.session_state:
                st.warning("🚫 Acesso negado. Você não tem permissão para acessar esta página.")
                st.stop()

            perfil = st.session_state.perfil.lower()

            db = DatabaseConnection()
            db.connect()
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT 1 FROM TB_012_ACESSOS
                WHERE LOWER(perfil) = ? AND id_modulo = ?
            """, perfil, id_modulo)

            if not cursor.fetchone():
                st.error("🚫 Acesso negado. Você não tem permissão para acessar esta página.")
                st.stop()

            return func(*args, **kwargs)
        return wrapper
    return decorador