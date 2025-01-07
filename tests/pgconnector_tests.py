#External imports
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import os

#Internal imports
from src.PGConnector.pgconnector import PGConnector


class TestPGConnector(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_database"
        self.connector = PGConnector(self.db_name)

    @patch('psycopg2.connect')
    def test_create_database(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Test case when the database does not exist
        mock_cursor.fetchone.return_value = None
        self.connector.create_database()
        mock_cursor.execute.assert_any_call(f"CREATE DATABASE \"{self.db_name}\"")

        # Test case when the database already exists
        mock_cursor.fetchone.return_value = (1,)
        self.connector.create_database()
        mock_cursor.execute.assert_any_call(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.db_name}'")

    @patch('psycopg2.connect')
    def test_connect(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        self.connector.connect()
        mock_connect.assert_called_once_with(
            host=self.connector.host,
            port=self.connector.port,
            database=self.db_name,
            user=self.connector.user,
            password=self.connector.password
        )
        self.assertTrue(self.connector.connection)
        self.assertTrue(self.connector.cursor)

    @patch('psycopg2.connect')
    @patch('os.listdir', return_value=['test_schema.sql'])
    @patch('builtins.open')
    def test_create_tables(self, mock_open_func, mock_listdir, mock_connect):
        mock_sql_content = "CREATE TABLE test_table (id INTEGER PRIMARY KEY);"
        mock_open_func.return_value.__enter__.return_value.read.return_value = mock_sql_content

        schema_dir = './schemas'
        expected_path = os.path.join(schema_dir, 'test_schema.sql')

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        self.connector.connect()
        self.connector.create_tables(schema_dir=schema_dir)

        # Test database usage
        mock_listdir.assert_called_once_with(schema_dir)
        mock_open_func.assert_called_once_with(expected_path, 'r')
        mock_cursor.execute.assert_called_once_with(mock_sql_content)
        mock_conn.commit.assert_called_once()

    @patch('psycopg2.connect')
    def test_insert_daily_price(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        self.connector.connect()

        # Insert daily price
        self.connector.insert_daily_price(
            coin_id="bitcoin",
            price_usd=50000.5,
            date="2024-01-01",
            full_response={"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
        )

        expected_query = """
            INSERT INTO cryptocurrency_daily_prices 
            (coin_id, price_usd, date, full_response) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (coin_id, date) DO UPDATE 
            SET price_usd = EXCLUDED.price_usd, 
                full_response = EXCLUDED.full_response;
            """
        mock_cursor.execute.assert_called_with(
            expected_query, ("bitcoin", 50000.5, "2024-01-01", '{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}')
        )
        mock_conn.commit.assert_called_once()

    @patch('psycopg2.connect')
    def test_update_monthly_aggregates(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        self.connector.connect()

        # Update monthly aggregates
        self.connector.update_monthly_aggregates(
            coin_id="bitcoin",
            date="2024-01-01",
            price_usd=50000.5
        )

        expected_query = """
            INSERT INTO cryptocurrency_monthly_aggregates 
            (coin_id, year, month, min_price, max_price) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (coin_id, year, month) DO UPDATE 
            SET min_price = LEAST(cryptocurrency_monthly_aggregates.min_price, EXCLUDED.min_price),
                max_price = GREATEST(cryptocurrency_monthly_aggregates.max_price, EXCLUDED.max_price);
            """
        mock_cursor.execute.assert_called_with(
            expected_query, ("bitcoin", 2024, 1, 50000.5, 50000.5)
        )
        mock_conn.commit.assert_called_once()



if __name__ == '__main__':
    unittest.main()
