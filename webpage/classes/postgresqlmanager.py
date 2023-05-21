import datetime
import psycopg2
from psycopg2 import sql

class PostgreSQLManager:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
    
    def get_all_data(self, table_name):
        with self.conn.cursor() as cursor:
            # Select all rows from the table for the given username
            select_query = sql.SQL("""
                SELECT * FROM {table_name}
            """).format(table_name=sql.Identifier(table_name))
            cursor.execute(select_query)

            # Fetch all the results
            user_data = cursor.fetchall()

            # Close the cursor and connection
            cursor.close()
            self.conn.close()

            return user_data
    
    def create_table(self, table_name, columns):
        with self.conn.cursor() as cursor:
            column_definitions = ', '.join(columns)
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {column_definitions}
                )
            """).format(
                table_name=sql.Identifier(table_name),
                column_definitions=sql.SQL(column_definitions)
            )
            cursor.execute(create_table_query)
        self.conn.commit()



    
    def insert_data(self, table_name, input_data_columns, input_data_values):
        with self.conn.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(input_data_columns))
            insert_query = sql.SQL("""
                INSERT INTO {table_name} ({column_names})
                VALUES ({placeholders})
            """).format(
                table_name=sql.Identifier(table_name),
                column_names=sql.SQL(', ').join(map(sql.Identifier, input_data_columns)),
                placeholders=sql.SQL(placeholders)
            )
            cursor.execute(insert_query, input_data_values)
        self.conn.commit()

    def get_data_from_date_range(self, table_name, from_date, to_date):
        with self.conn.cursor() as cursor:
            select_query = sql.SQL("""
                SELECT * FROM {table_name}
                WHERE datetime >= {from_date} AND datetime <= {to_date}
            """).format(
                table_name=sql.Identifier(table_name),
                from_date=sql.Literal(from_date),
                to_date=sql.Literal(to_date)
            )
            cursor.execute(select_query)

            data = cursor.fetchall()
            return data
