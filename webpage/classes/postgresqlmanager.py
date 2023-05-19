import datetime
import psycopg2
from psycopg2 import sql

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host='localhost',
    port='5858',
    user='postgres',
    password='password',
    database='mydatabase'
)

answer1 = 'question1'
answer2 = 'question2'
answer3 = 'question3'
answer4 = 'question4'

now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    user='postgres',
    password='password',
    database='mydatabase'
)

# Retrieve the username from the Flask session
username = 'tonto'

# Create a table name based on the username
table_name = f'user_{username}'

# Create the table if it doesn't exist
with conn.cursor() as cursor:
    create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {table_name} (
            datetime TIMESTAMP,
            question1 INTEGER,
            question2 INTEGER,
            question3 INTEGER,
            question4 INTEGER,
            total INTEGER
        )
    """).format(table_name=sql.Identifier(table_name))
    cursor.execute(create_table_query)

# Insert the data into the table
with conn.cursor() as cursor:
    insert_query = sql.SQL("""
        INSERT INTO {table_name} (datetime, question1, question2, question3, question4, total)
        VALUES (%s, %s, %s, %s, %s, %s)
    """).format(table_name=sql.Identifier(table_name))
    cursor.execute(insert_query, (current_time, answer1, answer2, answer3, answer4, int(answer1) + int(answer2) + int(answer3) + int(answer4)))

# Commit the transaction
conn.commit()

# Perform database operations
print("hola")

# Close the database connection when finished
conn.close()
