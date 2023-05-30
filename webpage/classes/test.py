import pandas as pd
import psycopg2




def main():

    # establish a connection to the db
    conn = psycopg2.connect(
        host = "localhost",
        port=5858,
        database = 'mydatabase',
        user = 'postgres',
        password = 'password')

    print("Connection to PostgreSQL created", "\n")

    # create a cursor out of a connection; a cursor allows you to communicate with Postgres and execute commands
    cur = conn.cursor()

    spark = initialize_Spark()

    df = loadDFWithSchema(spark)
    print(df.show())
    # df_cleaned = clean_drop_data(df)

    
    create_table(cur)

    data = {
        'name': ['Jordi'],
        'surname': ['Condom']
    }
    df = pd.DataFrame(data)

    insert_query, cars_seq = write_postgresql(df)

    cur.execute(insert_query, cars_seq)

    print("Data inserted into PostgreSQL", "\n")

    get_inserted_data(cur)
    
    cur.close()


    print("Commiting changes to database", "\n")
    # make sure that your changes are shown in the db
    conn.commit()

    print("Closing connection", "\n")

    # close the connection
    conn.close()

    print("Done!", "\n")


def initialize_Spark():

    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("CarbonFootprintCalculator") \
        .config("spark.driver.extraClassPath", "../drivers/postgresql_42.6.0.jar") \
        .config("spark.jars", "../drivers/postgresql_42.6.0.jar") \
        .getOrCreate()

    print("Spark Initialized", "\n")

    return spark

def loadDFWithoutSchema(spark):
    jdbc_url = "jdbc:postgresql://localhost:5858/mydatabase"

    df = spark.read.format("jdbc").option("url", jdbc_url) \
        .option("driver", "org.postgresql.Driver").option("dbtable", "test_table") \
        .option("user", "postgres").option("password", "password").load()

    return df

def loadDFWithSchema(spark):
    jdbc_url = "jdbc:postgresql://localhost:5858/mydatabase"
    connection_properties = {
        "user": "'postgres'",
        "password": "password",
        "driver": "org.postgresql.Driver"
    }

    schema = StructType([
        StructField("name", StringType(), True),
        StructField("surname", StringType(), True)
    ])
    
    #df = spark.read.format("jdbc").option("url", jdbc_url).option("dbtable", "mydatabase").options(connection_properties).schema(schema).load()

    df = spark.read.format("jdbc").option("url", jdbc_url) \
        .option("driver", "org.postgresql.Driver").option("dbtable", "test_table") \
        .option("user", "postgres").option("password", "password").load()

    print("Data loaded into PySpark", "\n")

    return df

def create_table(cursor):

    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table \
    (   name VARCHAR(255) NOT NULL, \
        surname VARCHAR(255) NOT NULL);")

        print("Created table in PostgreSQL", "\n")
    except:
        print("Something went wrong when creating the table", "\n")

def write_postgresql(df):
    cars_seq = [tuple(x) for x in df.to_records(index=False)]
    records_list_template = ','.join(['%s'] * len(cars_seq))
    insert_query = "INSERT INTO test_table (name, surname) VALUES {}".format(records_list_template)
    print("Inserting data into PostgreSQL...", "\n")
    return insert_query, cars_seq

def get_inserted_data(cursor):
    postgreSQL_select_Query = "SELECT * FROM test_table"
    cursor.execute(postgreSQL_select_Query)
    cars_records = cursor.fetchall()
    print(cars_records)



if __name__ == '__main__':
    main()