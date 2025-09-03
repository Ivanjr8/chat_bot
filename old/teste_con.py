# test_db_connection.py
import unittest
from db_connection import DatabaseConnection

class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseConnection()

    def test_has_connect_method(self):
        self.assertTrue(hasattr(self.db, 'connect'), "A classe não possui o método 'connect'.")

    def test_connect_method_callable(self):
        self.assertTrue(callable(self.db.connect), "'connect' não é um método chamável.")

    def test_connection_establishment(self):
        try:
            self.db.connect()
            self.assertIsNotNone(self.db.conn, "Conexão não foi estabelecida corretamente.")
        except Exception as e:
            self.fail(f"Erro ao conectar: {e}")

    def tearDown(self):
        if hasattr(self.db, 'close') and callable(self.db.close):
            self.db.close()

if __name__ == '__main__':
    unittest.main()