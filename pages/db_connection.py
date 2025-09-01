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
        return {
            "modulos": [row.pk_co_pergunta for row in cursor.execute("SELECT DISTINCT pk_co_pergunta FROM TB_007_PERGUNTAS")],
            "disciplinas": [
                {"id": row.pk_co_disciplina, "nome": row.no_disciplina}
                for row in cursor.execute("SELECT pk_co_disciplina, no_disciplina FROM TB_006_DISCIPLINA")
            ],
            "descritores": [
                {"id": row.pk_id_descritor, "tipo": row.co_tipo}
                for row in cursor.execute("SELECT pk_id_descritor, co_tipo FROM TB_005_DESCRITORES")
            ]
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
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def insert_resposta_completa(self, texto, alternativa, pergunta_id, correta):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TB_008_RESPOSTAS (NO_RESPOSTA, NO_ALTERNATIVA, FK_CO_PERGUNTA, CO_RESPOSTA_CORRETA)
            VALUES (?, ?, ?, ?)
        """, (texto, alternativa, pergunta_id, int(correta)))
        self.conn.commit()

    def update_resposta_completa(self, id_resposta, texto, alternativa, correta):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE TB_008_RESPOSTAS
            SET NO_RESPOSTA = ?, NO_ALTERNATIVA = ?, CO_RESPOSTA_CORRETA = ?
            WHERE CO_RESPOSTA = ?
        """, (texto, alternativa, int(correta), id_resposta))
        self.conn.commit()

    def delete_resposta(self, id_resposta):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM TB_008_RESPOSTAS WHERE CO_RESPOSTA = ?", (id_resposta,))
        self.conn.commit()

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
# professores
    
    
    
    

    # 🔍 Buscar escolas com filtro
    
    def buscar_professores(self, filtro_nome):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                a.PK_CO_PROFESSOR,
                a.NO_NOME_PROFESSOR,
                a.FK_ID_ESCOLA,
                a.FK_CO_DISCIPLINA,
                c.NO_ESCOLA
            FROM TB_013_PROFESSORES AS a
            INNER JOIN TB_006_DISCIPLINA AS b ON a.FK_CO_DISCIPLINA = b.PK_CO_DISCIPLINA
            INNER JOIN TB_002_ESCOLAS AS c ON a.FK_ID_ESCOLA = c.PK_ID_ESCOLA
            WHERE a.NO_NOME_PROFESSOR LIKE ?
        """, f"%{filtro_nome}%")

        columns = [column[0] for column in cursor.description]
        resultado = [dict(zip(columns, row)) for row in cursor.fetchall()]
        self.close()
        return resultado


    # 👥 Buscar professores por escola
    def buscar_professores_por_escola(self, id_escola):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT PK_ID_PROFESSOR, NO_NOME_PROFESSOR, FK_CO_DISCIPLINA
            FROM TB_013_PROFESSORES
            WHERE FK_ID_ESCOLA = ?
        """, id_escola)
        resultado = cursor.fetchall()
        self.close()
        return resultado

    # 📘 Buscar disciplinas
    def buscar_disciplinas(self):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT PK_CO_DISCIPLINA, NO_DISCIPLINA FROM TB_006_DISCIPLINA")
        resultado = cursor.fetchall()
        self.close()
        return resultado

    # ➕ Inserir professor
    def inserir_professor(self, nome, id_escola, id_disciplina):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TB_013_PROFESSORES (FK_ID_ESCOLA, NO_NOME_PROFESSOR, FK_CO_DISCIPLINA)
            VALUES (?, ?, ?)
        """, id_escola, nome, id_disciplina)
        self.conn.commit()
        self.close()

    # ✏️ Atualizar professor
    def atualizar_professor(self, id_professor, nome, id_disciplina):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE TB_013_PROFESSORES
            SET NO_NOME_PROFESSOR = ?, FK_CO_DISCIPLINA = ?
            WHERE PK_ID_PROFESSOR = ?
        """, nome, id_disciplina, id_professor)
        self.conn.commit()
        self.close()

    # ❌ Excluir professor
    def excluir_professor(self, id_professor):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM TB_013_PROFESSORES WHERE PK_ID_PROFESSOR = ?", id_professor)
        self.conn.commit()
        self.close()

# Disciplinas
    def disciplinas(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT PK_CO_DISCIPLINA, NO_DISCIPLINA FROM TB_006_DISCIPLINA"
            cursor.execute(query)
            resultados = cursor.fetchall()
            return [{"PK_CO_DISCIPLINA": r[0], "NO_DISCIPLINA": r[1].strip()} for r in resultados]
        except Exception as e:
            return []
# Descritores
    def descritores():
        from db_connection import DatabaseConnection  # ajuste conforme seu projeto

        db = DatabaseConnection()
        db.connect()

        cursor = db.conn.cursor()
        query = """
            SELECT PK_ID_DESCRITOR, FK_CO_DISCIPLINA, no_descritor
            FROM TB_005_DESCRITORES
        """
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        resultados = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        db.close()
        return resultados
# Perguntas
    def perguntas():
        from db_connection import DatabaseConnection  # ajuste conforme sua estrutura

        db = DatabaseConnection()
        db.connect()

        cursor = db.conn.cursor()
        query = """
            SELECT 
                PK_CO_PERGUNTA,
                NO_PERGUNTA,
                DE_PERGUNTA,
                FK_CO_DESCRITOR,
                FK_CO_DISCIPLINA
            FROM TB_007_PERGUNTAS
        """
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        resultados = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        db.close()
        return resultados

# Simulados

    def insert_simulado(co_simulado, fk_escola, fk_professor, fk_pergunta, fk_disciplina, fk_descritor):
        from db_connection import DatabaseConnection  # ajuste conforme sua estrutura

        db = DatabaseConnection()
        db.connect()

        cursor = db.conn.cursor()
        query = """
            INSERT INTO TB_014_SIMULADO (
                CO_SIMULADO,
                FK_CO_ESCOLA,
                FK_C_PROFESSOR,
                FK_CO_PERGUNTA,
                FK_CO_DISCIPLINA,
                FK_ID_DESCRITOR
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            co_simulado,
            fk_escola,
            fk_professor,
            fk_pergunta,
            fk_disciplina,
            fk_descritor
        ))
        db.conn.commit()
        cursor.close()
        db.close()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
# Escolas  

    def buscar_escolas():
        from db_connection import DatabaseConnection  # ajuste conforme sua estrutura

        db = DatabaseConnection()
        db.connect()

        cursor = db.conn.cursor()
        query = "SELECT PK_ID_ESCOLA, NO_ESCOLA FROM TB_002_ESCOLAS"
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        resultados = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        db.close()
        return resultados
# professores

    def professores(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT PK_CO_PROFESSOR, NO_NOME_PROFESSOR FROM TB_013_PROFESSORES")
        resultados = cursor.fetchall()
        return [{"id_professor": r[0], "nome": r[1]} for r in resultados]
    
    def professores_por_escola(self, escola_id):

        from db_connection import DatabaseConnection  # ajuste conforme sua estrutura

        db = DatabaseConnection()
        db.connect()
        
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        query = """
            SELECT 
                p.PK_CO_PROFESSOR,
                p.NO_NOME_PROFESSOR,
                e.PK_ID_ESCOLA,
                e.NO_ESCOLA
            FROM TB_013_PROFESSORES p
            JOIN TB_002_ESCOLAS e ON p.FK_ID_ESCOLA = e.PK_ID_ESCOLA
            WHERE p.FK_ID_ESCOLA = ?
        """
        cursor.execute(query, (escola_id,))
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    
    def get_professores(self):
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    a.FK_ID_ESCOLA,
                    a.NO_NOME_PROFESSOR,
                    a.FK_CO_DISCIPLINA,
                    c.NO_ESCOLA
                FROM TB_013_PROFESSORES AS a
                INNER JOIN TB_006_DISCIPLINA AS b ON a.FK_CO_DISCIPLINA = b.PK_CO_DISCIPLINA
                INNER JOIN TB_002_ESCOLAS AS c ON a.FK_ID_ESCOLA = c.PK_ID_ESCOLA
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            print(f"🔍 Registros encontrados: {len(resultados)}")

            return [
                {
                    "id_escola": r[0],
                    "nome": r[1],
                    "id_disciplina": r[2],
                    "nome_escola": r[3]
                }
                for r in resultados
            ]
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            return []


    
    def atualizar_professor(self, id_professor, nome, id_disciplina, id_escola):
        try:
            cursor = self.conn.cursor()
            query = """
                UPDATE TB_013_PROFESSORES
                SET NO_NOME_PROFESSOR = ?, FK_CO_DISCIPLINA = ?, FK_ID_ESCOLA = ?
                WHERE PK_CO_PROFESSOR = ?
            """
            cursor.execute(query, (nome, id_disciplina, id_escola, id_professor))
            self.conn.commit()
            return True
        except Exception as e:
            return str(e)
    
    def excluir_professor(self, id_professor):
        try:
            cursor = self.conn.cursor()
            query = "DELETE FROM TB_013_PROFESSORES WHERE PK_CO_PROFESSOR = ?"
            cursor.execute(query, (id_professor,))
            self.conn.commit()
            return True
        except Exception as e:
            return str(e)

    def buscar_disciplinas(self, filtro_nome=None):
        cursor = self.conn.cursor()
        query = "SELECT * from [dbo].[TB_006_DISCIPLINA]"
        params = []
        if filtro_nome:
            query += " AND NO_DISCIPLINA LIKE ?"
            params.append(f"%{filtro_nome}%")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

    def buscar_escolas():
            from db_connection import DatabaseConnection  # ajuste conforme sua estrutura

            db = DatabaseConnection()
            db.connect()

            cursor = db.conn.cursor()
            query = "SELECT PK_ID_ESCOLA, NO_ESCOLA FROM TB_002_ESCOLAS"
            cursor.execute(query)

            columns = [column[0] for column in cursor.description]
            resultados = [dict(zip(columns, row)) for row in cursor.fetchall()]

            cursor.close()
            db.close()
            return resultados

# ------------------------ escolas    
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
 
    def get_escola_por_id(self, id_escola):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT PK_ID_ESCOLA FROM TB_002_ESCOLAS WHERE PK_ID_ESCOLA = ?"
                cursor.execute(query, (id_escola,))
                return cursor.fetchone() is not None
            except Exception as e:
                st.error(f"Erro ao verificar ID: {e}")
                return False
            finally:
                conn.close()
        return False
    
    def insert_escola(self, id_escola,nome_escola):
        cursor = self.conn.cursor()
        cursor.execute("""
             INSERT INTO TB_002_ESCOLAS (PK_ID_ESCOLA, NO_ESCOLA)
             VALUES (?, ?)
        """, (id_escola, nome_escola))
        self.conn.commit()
        
    # def insert_escola(self, id_escola, nome_escola):
    #     try:
    #         conn = self.connect()
    #         if not conn:
    #             st.error("❌ Falha na conexão com o banco de dados.")
    #             return False

    #         with conn:
    #             cursor = conn.cursor()
    #             query = """
    #                 INSERT INTO TB_002_ESCOLAS (PK_ID_ESCOLA, NO_ESCOLA)
    #                 VALUES (?, ?)
    #             """
    #             cursor.execute(query, (id_escola.strip(), nome_escola.strip()))
    #         return True

    #     except Exception as e:
    #         st.error("❌ Erro ao inserir escola.")
    #         st.write(e)  # Exibe o erro técnico para depuração
    #         return False

    def update_escola(self, id_atual, novo_id=None, novo_nome=None):
        try:
            cursor = self.conn.cursor()

            # Monta dinamicamente o SQL com base nos campos que serão atualizados
            campos = []
            valores = []

            if novo_id and novo_id != id_atual:
                campos.append("PK_ID_ESCOLA = ?")
                valores.append(novo_id)

            if novo_nome:
                campos.append("NO_ESCOLA = ?")
                valores.append(novo_nome)

            # Se nenhum campo foi marcado, não faz nada
            if not campos:
                return False

            # Adiciona o ID atual para o WHERE
            valores.append(id_atual)

            sql = f"""
                UPDATE TB_002_ESCOLAS
                SET {', '.join(campos)}
                WHERE PK_ID_ESCOLA = ?
            """

            cursor.execute(sql, valores)
            self.conn.commit()
            return True

        except Exception as e:
            print("Erro ao atualizar escola:", e)
            return False

    def delete_escola(self, escola_id):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = "DELETE FROM TB_002_ESCOLAS WHERE PK_ID_ESCOLA = ?"
                cursor.execute(query, (escola_id,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                st.error(f"Erro ao excluir escola: {e}")
                return False
            finally:
                conn.close()
        return False


# Matriz

    def salvar_acessos(self, acessos_atualizados, df_acesso):
        if not acessos_atualizados:
            st.warning("⚠️ Nenhuma alteração de acesso foi feita.")
            return

        erros = []
        perfis_validos = set(df_acesso["perfil"].str.lower().str.strip().unique())
        cursor = self.conn.cursor()

        for item in acessos_atualizados:
            perfil = item.get("perfil", "").strip().lower()
            id_modulo = item.get("id_modulo")
            acesso = item.get("acesso", False)

            if perfil not in perfis_validos:
                erros.append(f"❌ Perfil inválido: {perfil}")
                continue

            try:
                if acesso:
                    cursor.execute("""
                        SELECT 1 FROM TB_012_ACESSOS WHERE LOWER(perfil) = ? AND id_modulo = ?
                    """, perfil, id_modulo)
                    existe = cursor.fetchone()

                    if not existe:
                        cursor.execute("""
                            INSERT INTO TB_012_ACESSOS (perfil, id_modulo)
                            VALUES (?, ?)
                        """, perfil, id_modulo)
                else:
                    st.write(f"Tentando deletar: perfil={perfil}, id_modulo={id_modulo}")
                    cursor.execute("""
                        DELETE FROM TB_012_ACESSOS WHERE LOWER(perfil) = ? AND id_modulo = ?
                    """, perfil, id_modulo)

            except Exception as e:
                erros.append(f"❌ Erro ao atualizar acesso de {perfil} ao módulo {id_modulo}: {e}")

        if erros:
            for erro in erros:
                st.warning(erro)
        else:
            try:
                self.conn.commit()
                st.success("✅ Acessos atualizados com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao salvar alterações no banco: {e}")    
                
class DatabaseTester:
    def __init__(self):
        try:
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
        except Exception as e:
            st.error(f"❌ Erro ao carregar configurações: {e}")
            self.connection_string = None

        self.conn = None

    def connect(self):
        if not self.connection_string:
            st.warning("⚠️ String de conexão não está definida.")
            return None
        try:
            self.conn = pyodbc.connect(self.connection_string)
            st.success("✅ Conexão estabelecida com sucesso!")
            return self.conn
        except Exception as e:
            st.error(f"❌ Erro ao conectar: {e}")
            return None

    def listar_tabelas(self):
        if not self.conn:
            st.warning("⚠️ Conexão não está ativa.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE 'TB%'")
            resultados = cursor.fetchall()

            if resultados:
                st.subheader("📋 Tabelas encontradas:")
                for row in resultados:
                    st.write(f"🔹 {row.name}")
            else:
                st.info("ℹ️ Nenhuma tabela encontrada com prefixo 'TB'.")
        except Exception as e:
            st.error(f"❌ Erro ao executar consulta: {e}")
        finally:
            cursor.close()
            self.conn.close()

def get_escola_por_id(self, id_escola):
    conn = self.connect()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM TB_002_ESCOLAS WHERE PK_ID_ESCOLA = ?"
            cursor.execute(query, (id_escola,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            st.error(f"Erro ao buscar escola: {e}")
            return None
        finally:
            conn.close()
    return None

    