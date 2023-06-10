import datetime
from pyspark.sql import functions as F

class SparkManager:
    def __init__(self, spark):
        self.spark = spark

''' JDBC stands for Java Database Connectivity. It is a Java API (Application Programming Interface) 
that allows Java programs to interact with relational databases. JDBC provides a set of classes and methods that
enable database operations such as connecting to a database, executing SQL queries, and retrieving and manipulating data '''

    def loadDF_with_tablename(self, table_name):
        # Load a DataFrame from a PostgreSQL table using JDBC

        jdbc_url = "jdbc:postgresql://0.0.0.0:5432/mydatabase"

        df = self.spark.read.format("jdbc").option("url", jdbc_url) \
            .option("driver", "org.postgresql.Driver").option("dbtable", table_name) \
            .option("user", "docker").option("password", "docker")\
            .option("numPartitions", 5) \
            .load()
        
        df = df.orderBy(F.col('start_date'))

        return 0, 0, df
    

    def fill_df(self, df):
        # Fill missing dates in a DataFrame with computed average values

        sum_days = df.select(F.sum('number_of_days')).first()[0]
        n_rows = df.count()

        # Compute the average per day for the other columns
        average_df = df.agg(
            (F.sum('diet') / sum_days).alias('average_diet'),
            (F.sum('car') / sum_days).alias('average_car'),
            (F.sum('bustrain') / sum_days).alias('average_bustrain'),
            (F.sum('housing') / sum_days).alias('average_housing'),
            (F.sum('consumption') / sum_days).alias('average_consumption'),
            (F.sum('waste') / sum_days).alias('average_waste'),
            (F.sum('shopping_profile') / n_rows).alias('average_shopping_profile'),
            (F.sum('refurbished') / n_rows).alias('average_refurbished'),
            (F.sum('plastic') / n_rows).alias('average_plastic'),
            (F.sum('glass') / n_rows).alias('average_glass'),
            (F.sum('paper') / n_rows).alias('average_paper'),
            (F.sum('aluminium') / n_rows).alias('average_aluminium'),
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
        average_shopping_profile = average_row['average_shopping_profile']
        average_refurbished = average_row['average_refurbished']
        average_plastic = average_row['average_plastic']
        average_glass = average_row['average_glass']
        average_paper = average_row['average_paper']
        average_aluminium = average_row['average_aluminium']

        # Convert the date columns to a Pandas DataFrame
        # Create a list of date pairs from the Pandas DataFrame

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
                shopping_profile = average_shopping_profile
                refurbished = average_refurbished
                plastic = average_plastic
                glass = average_glass
                paper = average_paper
                aluminium = average_aluminium
                transportation = car + bustrain
                total = diet + transportation + housing + consumption + waste
                plane = 0
                average_per_day = total/number_of_days

                # Append the filled date pair to the result list
                consecutive_date_pairs_filled.append((start_date, end_date, diet, transportation, car, bustrain, plane, housing, consumption, 
                                                      shopping_profile,refurbished,waste,plastic,glass,paper, aluminium,number_of_days, average_per_day, total))
            # Set the start_date and end_date for the next iteration
            start_date, end_date = next_start_date, next_end_date

        # Define the column names for the filled dates DataFrame
        columns = ['start_date', 'end_date', 'diet', 'transportation', 'car', 'bustrain', 'plane', 'housing', 'consumption',
                   'shopping_profile', 'refurbished', 'waste', 'plastic', 'glass', 'paper', 'aluminium' 'number_of_days', 'average_per_day', 'total']

        if consecutive_date_pairs_filled:
            # Create a DataFrame from the filled consecutive date pairs
            filled_dates_df = self.spark.createDataFrame(consecutive_date_pairs_filled, columns)

            num_partitions = 30
            print('num_partitions: ', num_partitions)

            # Repartition the original DataFrame and the filled dates DataFrame
            df_partitioned = df.repartition(num_partitions, "start_date")
            filled_dates_partitioned = filled_dates_df.repartition(num_partitions, "start_date")

            # Join the partitioned DataFrames
            joined_df = df_partitioned.union(filled_dates_partitioned)

            # Order the rows by start_date
            ordered_df = joined_df.orderBy(F.col('start_date'))

            print(ordered_df.show())

            return ordered_df
        
        else:
            # If there are no consecutive date pairs to fill, return the original DataFrame
            return df

        
        