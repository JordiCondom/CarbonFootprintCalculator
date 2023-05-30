from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, LongType, TimestampType, ShortType, DateType
from pyspark.sql.functions import col

class SparkManager:
    def __init__(self, spark):
        self.spark = spark


    def loadDF_with_tablename_and_dates(self, table_name, from_date, to_date):
        jdbc_url = "jdbc:postgresql://localhost:5858/mydatabase"

        query = f"""
        SELECT start_date
        FROM {table_name}
        WHERE end_date >= '{from_date}' AND start_date <= '{to_date}'
        """

        query_min_max = f"""
        SELECT Min(start_date),
            Max(start_date)
        FROM ({query}) s
        """

        # Determine min and maximum values
        df_min_max = self.spark.read.format("jdbc").option("url", jdbc_url) \
            .option("driver", "org.postgresql.Driver").option("dbtable", f"({query_min_max}) t") \
            .option("user", "postgres").option("password", "password").load()
        
        min_date = df_min_max.collect()[0]['min']
        max_date = df_min_max.collect()[0]['max']

        df = self.spark.read.format("jdbc").option("url", jdbc_url) \
            .option("driver", "org.postgresql.Driver").option("dbtable", table_name) \
            .option("user", "postgres").option("password", "password") \
            .option("partitionColumn", "start_date") \
            .option("numPartitions", 10) \
            .option("lowerBound", min_date) \
            .option("upperBound", max_date) \
            .load()

        return df


    def loadDF_with_tablename(self, table_name):
        
        jdbc_url = "jdbc:postgresql://localhost:5858/mydatabase"

        query = f"""
        SELECT start_date
        FROM   {table_name}
        """

        query_min_max = f"""
        SELECT Min(start_date),
            Max(start_date)
        FROM   ({query}) s
        """

        # Determine min and maximum values
        df_min_max = self.spark.read.format("jdbc").option("url",jdbc_url) \
            .option("driver", "org.postgresql.Driver").option("dbtable", f"({query_min_max}) t") \
            .option("user", "postgres").option("password", "password").load()
        
        min_date = df_min_max.collect()[0]['min']
        max_date = df_min_max.collect()[0]['max']


        df = self.spark.read.format("jdbc").option("url", jdbc_url) \
            .option("driver", "org.postgresql.Driver").option("dbtable", table_name) \
            .option("user", "postgres").option("password", "password")\
            .option("partitionColumn", "start_date") \
            .option("numPartitions", 10) \
            .option("lowerBound", min_date) \
            .option("upperBound", max_date) \
            .load()

        return min_date, max_date, df