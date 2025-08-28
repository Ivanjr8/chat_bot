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
  # Perguntas  
  
    def get_filtros_perguntas(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT DISTINCT PK_CO_PERGUNTA FROM TB_007_PERGUNTAS")
        modulos = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT PK_CO_DISCIPLINA, NO_DISCIPLINA FROM TB_006_DISCIPLINA")
        disciplinas = [{"id": row[0], "nome": row[1].strip()} for row in cursor.fetchall()]

        cursor.execute("SELECT PK_ID_DESCRITOR, CO_TIPO FROM TB_005_DESCRITORES")
        descritores = [{"id": row[0], "tipo": row[1].strip()} for row in cursor.fetchall()]

        return {
            "modulos": modulos,
            "disciplinas": disciplinas,
            "descritores": descritores
        }

    def get_perguntas(self, filtro_modulo=None, filtro_disciplina=None, filtro_descritor=None):
        cursor = self.conn.cursor()
        query = """
            SELECT a.PK_CO_PERGUNTA, a.NO_PERGUNTA, a.DE_PERGUNTA,
                   b.NO_DISCIPLINA, c.CO_TIPO
            FROM TB_007_PERGUNTAS AS a
            INNER JOIN TB_006_DISCIPLINA AS b ON a.FK_CO_DISCIPLINA = b.PK_CO_DISCIPLINA
            INNER JOIN TB_005_DESCRITORES AS c ON a.FK_CO_DESCRITOR = c.PK_ID_DESCRITOR
            WHERE 1=1
        """
        params = []

        if filtro_modulo:
            query += " AND a.PK_CO_PERGUNTA = ?"
            params.append(filtro_modulo)

        if filtro_disciplina:
            query += " AND b.PK_CO_DISCIPLINA = ?"
            params.append(filtro_disciplina)

        if filtro_descritor:
            query += " AND c.PK_ID_DESCRITOR = ?"
            params.append(filtro_descritor)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        return [dict(zip(col_names, row)) for row in rows]

    def insert_pergunta(self, titulo, descricao, id_disciplina, id_descritor):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TB_007_PERGUNTAS (NO_PERGUNTA, DE_PERGUNTA, FK_CO_DISCIPLINA, FK_CO_DESCRITOR)
            VALUES (?, ?, ?, ?)
        """, (titulo, descricao, id_disciplina, id_descritor))
        self.conn.commit()

    def update_pergunta(self, id_pergunta, titulo, descricao, id_disciplina, id_descritor):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE TB_007_PERGUNTAS
            SET NO_PERGUNTA = ?, DE_PERGUNTA = ?, FK_CO_DISCIPLINA = ?, FK_CO_DESCRITOR = ?
            WHERE PK_CO_PERGUNTA = ?
        """, (titulo, descricao, id_disciplina, id_descritor, id_pergunta))
        self.conn.commit()

    def delete_pergunta(self, id_pergunta):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM TB_007_PERGUNTAS WHERE PK_CO_PERGUNTA = ?", (id_pergunta,))
        self.conn.commit()

        
# Respostas

    def get_respostas_com_filtros(self, modulo=None, disciplina=None, descritor=None):
        cursor = self.conn.cursor()
        query = """
            SELECT b.pk_co_pergunta, b.no_pergunta, b.de_pergunta,
                a.co_resposta, a.no_resposta, a.no_alternativa, a.co_resposta_correta,
                c.co_tipo, d.pk_co_disciplina, d.no_disciplina
            FROM TB_008_RESPOSTAS AS a
            INNER JOIN TB_007_PERGUNTAS AS b ON a.fk_co_pergunta = b.pk_co_pergunta
            INNER JOIN TB_005_DESCRITORES AS c ON b.fk_co_descritor = c.pk_id_descritor
            INNER JOIN TB_006_DISCIPLINA AS d ON b.fk_co_disciplina = d.pk_co_disciplina
            WHERE 1=1
        """
        params = []

        if modulo:
            query += " AND b.pk_co_pergunta = ?"
            params.append(modulo)
        if disciplina:
            query += " AND d.pk_co_disciplina = ?"
            params.append(disciplina)
        if descritor:
            query += " AND c.pk_id_descritor = ?"
            params.append(descritor)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        return [dict(zip(col_names, row)) for row in rows]



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

# Escolas        
    def get_escolas(self, filtro_nome=None):
        cursor = self.conn.cursor()
        query = "SELECT PK_ID_ESCOLA, NO_ESCOLA FROM TB_002_ESCOLAS WHERE 1=1"
        params = []
        if filtro_nome:
            query += " AND NO_ESCOLA LIKE ?"
            params.append(f"%{filtro_nome}%")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

    def insert_escola(self, nome_escola):
        cursor = self.conn.cursor()
        query = """
            INSERT INTO TB_002_ESCOLAS (NO_ESCOLA)
            OUTPUT INSERTED.PK_ID_ESCOLA
            VALUES (?)
        """
        cursor.execute(query, (nome_escola,))
        escola_id = cursor.fetchone()[0]
        self.conn.commit()
        return escola_id

    def update_escola(self, escola_id, novo_nome):
        cursor = self.conn.cursor()
        query = "UPDATE TB_002_ESCOLAS SET NO_ESCOLA = ? WHERE PK_ID_ESCOLA = ?"
        cursor.execute(query, (novo_nome, escola_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_escola(self, escola_id):
        cursor = self.conn.cursor()
        query = "DELETE FROM TB_002_ESCOLAS WHERE PK_ID_ESCOLA = ?"
        cursor.execute(query, (escola_id,))
        self.conn.commit()
        return cursor.rowcount > 0

        
        