# db_connection.py
import pyodbc
import streamlit as st

# Conexão com a base de dados
class DatabaseConnection:
    def __init__(self):
        db = st.secrets["database"]
        self.connection_string = (
            f"DRIVER={{{db['driver']}}};"
            f"SERVER={db['server']};"
            f"DATABASE={db['database']};"
            f"UID={db['uid']};"
            f"PWD={db['pwd']};"
            f"Encrypt={db['encrypt']};"
            f"TrustServerCertificate={db['trust_cert']};"
            f"Connection Timeout={db['timeout']};"
        )
        self.conn = None

    def connect(self):
        self.conn = pyodbc.connect(self.connection_string)

    def close(self):
        if self.conn:
            self.conn.close()
    
    def get_modulos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT PK_CO_PERGUNTA FROM TB_007_PERGUNTAS ORDER BY PK_CO_PERGUNTA")
        modulos = [str(row[0]) for row in cursor.fetchall()]
        cursor.close()
        return modulos
    
    def get_perguntas(self, filtro_modulo=None):
        cursor = self.conn.cursor()
        if filtro_modulo:
            cursor.execute(
                "SELECT PK_CO_PERGUNTA, CO_PERGUNTA, DE_PERGUNTA FROM TB_007_PERGUNTAS WHERE PK_CO_PERGUNTA = ?",
                (filtro_modulo,)
            )
        else:
            cursor.execute("SELECT PK_CO_PERGUNTA, CO_PERGUNTA, DE_PERGUNTA FROM TB_007_PERGUNTAS")

        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return rows


    def insert_pergunta(self, codigo, descricao):
        cursor = self.conn.cursor()
        cursor.execute(
        "INSERT INTO TB_007_PERGUNTAS (CO_PERGUNTA, DE_PERGUNTA) VALUES (?, ?)",
        codigo, descricao
    )
        self.conn.commit()
        cursor.close()

    def update_pergunta(self, id, codigo, descricao):
        cursor = self.conn.cursor()
        cursor.execute(
        "UPDATE TB_007_PERGUNTAS SET CO_PERGUNTA = ?, DE_PERGUNTA = ? WHERE PK_CO_PERGUNTA = ?",
        codigo, descricao, id
    )
        self.conn.commit()
        cursor.close()


    def delete_pergunta(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM TB_007_PERGUNTAS WHERE PK_CO_PERGUNTA = ?", id)
        self.conn.commit()
        cursor.close()
        
# Respostas
    def get_respostas(self, pergunta_id=None):
        cursor = self.conn.cursor()
        if pergunta_id:
            cursor.execute("""
                SELECT CO_RESPOSTA, NO_RESPOSTA, FK_CO_PERGUNTA, CO_RESPOSTA_CORRETA
                FROM TB_008_RESPOSTAS WHERE FK_CO_PERGUNTA = ?
            """, pergunta_id)
        else:
            cursor.execute("SELECT CO_RESPOSTA, NO_RESPOSTA, FK_CO_PERGUNTA, CO_RESPOSTA_CORRETA FROM TB_008_RESPOSTAS")
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return rows

    def insert_resposta(self, texto_resposta, pergunta_id, resposta_correta):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TB_008_RESPOSTAS (NO_RESPOSTA, FK_CO_PERGUNTA, CO_RESPOSTA_CORRETA)
            VALUES (?, ?, ?)
        """, texto_resposta, pergunta_id, resposta_correta)
        self.conn.commit()
        cursor.close()

    def update_resposta(self, resposta_id, texto_resposta, pergunta_id, resposta_correta):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE TB_008_RESPOSTAS
            SET NO_RESPOSTA = ?, FK_CO_PERGUNTA = ?, CO_RESPOSTA_CORRETA = ?
            WHERE CO_RESPOSTA = ?
        """, texto_resposta, pergunta_id, resposta_correta, resposta_id)
        self.conn.commit()
        cursor.close()

    def delete_resposta(self, resposta_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM TB_008_RESPOSTAS WHERE CO_RESPOSTA = ?", resposta_id)
        self.conn.commit()
        cursor.close()
    
    # 🔐 Autenticação
    def autenticar_usuario(self,usuario, senha):
        cursor = self.conn.cursor()
        cursor.execute("SELECT perfil FROM TB_010_USUARIOS WHERE usuario=? AND senha=?", (usuario, senha))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    
    def listar_usuarios(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT usuario FROM TB_010_USUARIOS ORDER BY usuario")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
    
    def merge_usuario(self, usuario, senha, perfil):
        cursor = self.conn.cursor()
        try:
            # Verifica se o usuário já existe
            cursor.execute("SELECT id FROM TB_010_USUARIOS WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()

            if resultado:
                # Atualiza usuário existente
                cursor.execute("""
                    UPDATE TB_010_USUARIOS
                    SET senha = ?, perfil = ?
                    WHERE usuario = ?
                """, (senha, perfil, usuario))
                self.conn.commit()
                return "atualizado"
            else:
                # Insere novo usuário
                cursor.execute("""
                    INSERT INTO TB_010_USUARIOS (usuario, senha, perfil)
                    VALUES (?, ?, ?)
                """, (usuario, senha, perfil))
                self.conn.commit()
                return "inserido"
        except Exception as e:
            return f"erro: {str(e)}"
        finally:
            cursor.close()
    
    def get_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, usuario, perfil FROM TB_010_USUARIOS ORDER BY usuario")
        usuarios = [{"id": row[0], "usuario": row[1], "perfil": row[2]} for row in cursor.fetchall()]
        cursor.close()
        return usuarios

    def delete_usuario(self, usuario):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM TB_010_USUARIOS WHERE usuario = ?", (usuario,))
            self.conn.commit()
            return True
        except Exception as e:
            return f"erro: {str(e)}"
        finally:
            cursor.close()
            
   # def get_modulos(self):
    #    cursor = self.conn.cursor()
    #    cursor.execute("SELECT id, nome FROM TB_011_MODULOS")
    #    modulos = [{"id": row[0], "nome": row[1]} for row in cursor.fetchall()]
   #     cursor.close()
    #    return modulos

    def get_acessos_usuario(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT modulo_id FROM TB_012_ACESSOS
            WHERE usuario_id = ? AND permitido = 1
        """, (usuario_id,))
        acessos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return acessos

    def set_acesso(self, usuario_id, modulo_id, permitido):
        cursor = self.conn.cursor()
        cursor.execute("""
            MERGE TB_012_ACESSOS AS target
            USING (SELECT ? AS usuario_id, ? AS modulo_id) AS source
            ON target.usuario_id = source.usuario_id AND target.modulo_id = source.modulo_id
            WHEN MATCHED THEN
                UPDATE SET permitido = ?
            WHEN NOT MATCHED THEN
                INSERT (usuario_id, modulo_id, permitido)
                VALUES (?, ?, ?);
        """, (usuario_id, modulo_id, permitido, usuario_id, modulo_id, permitido))
        self.conn.commit()
        cursor.close()
        
    def usuario_tem_acesso(self, usuario_id, nome_modulo):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM TB_012_ACESSOS A
            JOIN TB_011_MODULOS M ON A.modulo_id = M.id
            WHERE A.usuario_id = ? AND M.nome = ? AND A.permitido = 1
        """, (usuario_id, nome_modulo))
        resultado = cursor.fetchone()[0]
        cursor.close()
        return resultado > 0
    def get_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, usuario FROM TB_010_USUARIOS ORDER BY usuario")
        usuarios = [{"id": row[0], "usuario": row[1]} for row in cursor.fetchall()]
        cursor.close()
        return usuarios

    #def get_modulos(self):
    #    cursor = self.conn.cursor()
    #    cursor.execute("SELECT id, nome FROM TB_011_MODULOS ORDER BY nome")
    #    modulos = [{"id": row[0], "nome": row[1]} for row in cursor.fetchall()]
    #    cursor.close()
    #    return modulos

    def get_acessos_usuario(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT modulo_id FROM TB_012_ACESSOS
            WHERE usuario_id = ? AND permitido = 1
        """, (usuario_id,))
        acessos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return acessos

    def set_acesso(self, usuario_id, modulo_id, permitido):
        cursor = self.conn.cursor()
        cursor.execute("""
            MERGE TB_012_ACESSOS AS target
            USING (SELECT ? AS usuario_id, ? AS modulo_id) AS source
            ON target.usuario_id = source.usuario_id AND target.modulo_id = source.modulo_id
            WHEN MATCHED THEN
                UPDATE SET permitido = ?
            WHEN NOT MATCHED THEN
                INSERT (usuario_id, modulo_id, permitido)
                VALUES (?, ?, ?);
        """, (usuario_id, modulo_id, permitido, usuario_id, modulo_id, permitido))
        self.conn.commit()
        cursor.close()