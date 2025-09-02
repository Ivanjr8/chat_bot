import unittest
from unittest.mock import MagicMock
from decoradores import acesso_restrito
from db_connection import DatabaseConnection
import streamlit as st
from decoradores import acesso_restrito
import pandas as pd
import math
from db_connection import DatabaseConnection

db = DatabaseConnection()

#from seu_modulo import Database  # substitua pelo nome real do seu módulo

class TestSalvarResultadoResposta(unittest.TestCase):

    def setUp(self):
        # Simula uma conexão e cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

        # Instancia a classe com a conexão mockada
        self.db = DatabaseConnection(self.mock_conn)

    def test_insercao_com_tentativa_existente(self):
        # Simula que já existe uma tentativa anterior
        self.mock_cursor.fetchone.return_value = [2]  # última tentativa = 2

        self.db.salvar_resultado_resposta(
            pergunta_id=10,
            resposta_aluno='B',
            disciplina_id=3,
            correta=1,
            co_simulado=7,
            aluno_id=42
        )

        # Verifica se o SELECT foi chamado corretamente
        self.mock_cursor.execute.assert_any_call("""
        SELECT MAX(CO_TENTATIVA)
        FROM dbo.TB_009_RESULTADOS
        WHERE FK_CO_SIMULADO = ? AND FK_ID_ALUNO = ?
        """, (7, 42))

        # Verifica se o INSERT foi chamado com tentativa = 3
        self.mock_cursor.execute.assert_any_call("""
        INSERT INTO dbo.TB_009_RESULTADOS (
            FK_CO_PERGUNTA,
            CO_RESPOSTA_ALUNO,
            FK_CO_DISCIPLINA,
            CO_RESPOSTA_CORRETA,
            FK_CO_SIMULADO,
            FK_ID_ALUNO,
            CO_TENTATIVA
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (10, 'B', 3, 1, 7, 42, 3))

    def test_insercao_sem_tentativa_anterior(self):
        # Simula que não existe tentativa anterior
        self.mock_cursor.fetchone.return_value = [None]

        self.db.salvar_resultado_resposta(
            pergunta_id=5,
            resposta_aluno='C',
            disciplina_id=2,
            correta=0,
            co_simulado=9,
            aluno_id=99
        )

        # Verifica se o INSERT foi chamado com tentativa = 1
        self.mock_cursor.execute.assert_any_call("""
        INSERT INTO dbo.TB_009_RESULTADOS (
            FK_CO_PERGUNTA,
            CO_RESPOSTA_ALUNO,
            FK_CO_DISCIPLINA,
            CO_RESPOSTA_CORRETA,
            FK_CO_SIMULADO,
            FK_ID_ALUNO,
            CO_TENTATIVA
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (5, 'C', 2, 0, 9, 99, 1))

    def test_commit_chamado(self):
        self.mock_cursor.fetchone.return_value = [1]
        self.db.salvar_resultado_resposta(1, 'A', 1, 1, 1, 1)
        self.mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()