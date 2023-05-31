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
    
    def close_connection(self):
        self.conn.close()

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

    def insert_data(self, table_name, response_data):
        input_data_columns = [key.lower() for key in response_data.keys()]
        input_data_values = list(response_data.values())

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
                WHERE start_date >= {from_date} AND end_date <= {to_date}
            """).format(
                table_name=sql.Identifier(table_name),
                from_date=sql.Literal(from_date),
                to_date=sql.Literal(to_date)
            )
            cursor.execute(select_query)

            data = cursor.fetchall()
            return data
        

    def delete_table_sample_by_dates(self, table_name, start_date, end_date):
        with self.conn.cursor() as cursor:
            delete_query = sql.SQL("""
                DELETE FROM {table_name}
                WHERE start_date = {start} AND end_date = {end}
            """).format(
                table_name=sql.Identifier(table_name),
                start=sql.Literal(start_date),
                end=sql.Literal(end_date)
            )
            cursor.execute(delete_query)
        self.conn.commit()

    def delete_all_table_data(self, table_name):
        with self.conn.cursor() as cursor:
            delete_query = sql.SQL("""
                DELETE FROM {table_name}
            """).format(table_name=sql.Identifier(table_name))
            cursor.execute(delete_query)
        self.conn.commit()
