import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, LongType, TimestampType, ShortType, DateType
from pyspark.sql.functions import col
from pyspark.sql import functions as F
from pyspark.sql.window import Window

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
            .option("numPartitions", 5) \
            .option("lowerBound", min_date) \
            .option("upperBound", max_date) \
            .load()

        return df


    def loadDF_with_tablename(self, table_name):
        jdbc_url = "jdbc:postgresql://localhost:5858/mydatabase"

        df = self.spark.read.format("jdbc").option("url", jdbc_url) \
            .option("driver", "org.postgresql.Driver").option("dbtable", table_name) \
            .option("user", "postgres").option("password", "password")\
            .option("numPartitions", 5) \
            .load()
        
        df = df.orderBy(F.col('start_date'))

        return 0, 0, df
    

    def fill_df(self, df):
        sum_days = df.select(F.sum('number_of_days')).first()[0]

        # Compute the average per day for the other columns
        average_df = df.agg(
            (F.sum('diet') / sum_days).alias('average_diet'),
            (F.sum('car') / sum_days).alias('average_car'),
            (F.sum('bustrain') / sum_days).alias('average_bustrain'),
            (F.sum('housing') / sum_days).alias('average_housing'),
            (F.sum('consumption') / sum_days).alias('average_consumption'),
            (F.sum('waste') / sum_days).alias('average_waste')
        )

        # Retrieve the average per day values
        average_row = average_df.first()

        # Retrieve the individual averages
        average_diet = average_row['average_diet']
        average_car = average_row['average_car']
        average_bustrain = average_row['average_bustrain']
        average_housing = average_row['average_housing']
        average_consumption = average_row['average_consumption']
        average_waste = average_row['average_waste'] 

        date_columns = df.select("start_date", "end_date")

        date_columns = date_columns.toPandas()

        # Create a list of date pairs from the Pandas DataFrame
        date_pairs = list(zip(date_columns["start_date"], date_columns["end_date"]))

        consecutive_date_pairs_filled = []

        start_date, end_date = date_pairs[0]
        for next_start_date, next_end_date in date_pairs[1:]:
            # Add the existing date pair to the result list
            #consecutive_date_pairs.append((start_date, end_date))
            
            # Generate a pair for the range of dates between the current pair and the next pair
            start_date = end_date + datetime.timedelta(days=1)
            end_date = next_start_date - datetime.timedelta(days=1)
            if start_date <= end_date:
                number_of_days = (end_date - start_date).days
                diet = average_diet*number_of_days
                car = average_car*number_of_days
                bustrain = average_bustrain*number_of_days
                housing = average_housing*number_of_days
                consumption = average_consumption*number_of_days
                waste = average_waste*number_of_days
                transportation = car + bustrain
                total = diet + transportation + housing + consumption + waste
                plane = 0
                average_per_day = total/number_of_days
                consecutive_date_pairs_filled.append((start_date, end_date, diet, transportation, car, bustrain, plane, housing, consumption, waste, number_of_days, average_per_day, total))

            start_date, end_date = next_start_date, next_end_date

        columns = ['start_date', 'end_date', 'diet', 'transportation', 'car', 'bustrain', 'plane', 'housing', 'consumption', 'waste', 'number_of_days', 'average_per_day', 'total']
        filled_dates_df = self.spark.createDataFrame(consecutive_date_pairs_filled, columns)

        num_partitions = 30
        print('num_partitions: ', num_partitions)
        df_partitioned = df.repartition(num_partitions, "start_date")
        filled_dates_partitioned = filled_dates_df.repartition(num_partitions, "start_date")

        # Join the partitioned DataFrames
        joined_df = df_partitioned.union(filled_dates_partitioned)

        # Order the rows by start_date
        ordered_df = joined_df.orderBy(F.col('start_date'))

        print(ordered_df.show())

        return ordered_df
        