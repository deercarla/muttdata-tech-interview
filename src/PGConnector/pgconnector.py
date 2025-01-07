import os
import psycopg2
from dotenv import load_dotenv
import logging
import json
from datetime import datetime
import pandas as pd

class PGConnector:
    def __init__(self, db_name, port=5432):
        """
        Initialize the PostgreSQL connection.

        :param db_name: Name of the database to connect to
        :param port: Port number (default 5432)
        """
        load_dotenv()
        self.host = os.getenv('PG_HOST', 'localhost')
        self.port = os.getenv('PG_PORT', port)
        self.user = os.getenv('PG_USER')
        self.password = os.getenv('PG_PASSWORD')
        self.db_name = db_name

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.connection = None
        self.cursor = None

    def create_database(self):
        """
        Create the database if it doesn't exist.
        """
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            connection.autocommit = True
            cursor = connection.cursor()

            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.db_name}'")
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f'CREATE DATABASE "{self.db_name}"')
                self.logger.info(f"Database {self.db_name} created successfully")
            else:
                self.logger.info(f"Database {self.db_name} already exists")

            cursor.close()
            connection.close()

        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Error creating database: {error}")


    def connect(self):
        """
        Establish a connection to the PostgreSQL database.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = False  # Start with transactions off
            self.cursor = self.connection.cursor()
            self.logger.info(f"Successfully connected to database {self.db_name}")
        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Error connecting to PostgreSQL: {error}")


    def create_tables(self, schema_dir='./schemas'):
        """
        Create tables using SQL files in the specified directory.

        :param schema_dir: Directory containing SQL schema files
        """
        if not self.connection:
            raise Exception("Database connection not established. Call connect() first.")

        try:
            schema_files = [f for f in os.listdir(schema_dir) if f.endswith('.sql')]

            for schema_file in schema_files:
                file_path = os.path.join(schema_dir, schema_file)
                with open(file_path, 'r') as f:
                    sql_script = f.read()
                    self.cursor.execute(sql_script)

            self.connection.commit()
            self.logger.info("Tables created successfully")
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            self.logger.error(f"Error creating tables: {error}")


    def insert_daily_price(self, coin_id, price_usd, date, full_response):
        """
        Insert daily cryptocurrency price data.

        :param coin_id: Identifier for the cryptocurrency
        :param price_usd: Price in USD
        :param date: Date of the price
        :param full_response: Full JSON response (dict or JSON-serializable object)
        """
        try:
            json_response = json.dumps(full_response)

            insert_query = """
            INSERT INTO cryptocurrency_daily_prices 
            (coin_id, price_usd, date, full_response) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (coin_id, date) DO UPDATE 
            SET price_usd = EXCLUDED.price_usd, 
                full_response = EXCLUDED.full_response;
            """
            self.cursor.execute(insert_query, (coin_id, price_usd, date, json_response))
            self.connection.commit()
            self.logger.info(f"Inserted daily price for {coin_id} on {date}")
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            self.logger.error(f"Error inserting daily price: {error}")


    def update_monthly_aggregates(self, coin_id, date, price_usd):
        """
        Update monthly aggregates for a given coin and date.

        :param coin_id: Identifier for the cryptocurrency
        :param date: Date of the price
        :param price_usd: Price in USD
        """
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month

            upsert_query = """
            INSERT INTO cryptocurrency_monthly_aggregates 
            (coin_id, year, month, min_price, max_price) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (coin_id, year, month) DO UPDATE 
            SET min_price = LEAST(cryptocurrency_monthly_aggregates.min_price, EXCLUDED.min_price),
                max_price = GREATEST(cryptocurrency_monthly_aggregates.max_price, EXCLUDED.max_price);
            """

            self.cursor.execute(upsert_query, (coin_id, year, month, price_usd, price_usd))
            self.connection.commit()
            self.logger.info(f"Updated monthly aggregates for {coin_id} in {year}-{month}")
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            self.logger.error(f"Error updating monthly aggregates: {error}")


    def close_connection(self):
        """
        Close database connection and cursor.
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            self.logger.error(f"Error updating monthly aggregates: {error}")


    ################# For Task 3 only  #################
    def execute_sql_file(self, sql_file_path):
        """
        Execute an SQL file to set up tables and insert data.

        :param sql_file_path: Path to the SQL file to execute
        """
        if not self.connection:
            raise Exception("Database connection not established. Call connect() first.")

        try:
            with open(sql_file_path, 'r') as file:
                sql_script = file.read()
                self.cursor.execute(sql_script)
            self.connection.commit()
            self.logger.info(f"Executed SQL file: {sql_file_path}")
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            self.logger.error(f"Error executing SQL file: {error}")

    def query_coin_data(self, query):
        """
        Executes a query and returns the result as a pandas DataFrame.

        :param query: SQL query string
        :return: DataFrame with query results
        """
        try:
            if not self.connection:
                raise Exception("Database connection not established. Call connect() first.")

            df = pd.read_sql(query, self.connection)
            return df

        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Error executing query: {error}")
            return pd.DataFrame()
