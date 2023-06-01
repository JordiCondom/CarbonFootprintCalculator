import base64
import io
import json
import os
from datetime import datetime, timedelta
import time
from flask import Flask, redirect, render_template, request, session, make_response
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import plotly
from classes.airportFootprintManager import AirportFootprintManager
from classes.datesManager import DatesManager
from classes.footprintcalculator import footprintCalculator
from classes.graphcreator import graphCreator
from classes.mongodbmanager import MongoDBManager
import psycopg2
from psycopg2 import sql
from pyspark.sql.functions import col
from pyspark.sql import SparkSession
import plotly.graph_objects as go
import pyspark.sql.functions as F
import plotly.express as px
from pyspark.sql.functions import col, expr, date_add, lit, min, max
from pyspark.sql.types import DateType
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, lead, col

from classes.postgresqlmanager import PostgreSQLManager
from classes.redismanager import RedisManager
from classes.sparkmanager import SparkManager

session_cookie_path = './session_cookie'
if os.path.exists(session_cookie_path):
    os.remove('flask_session')

with open('./co2EmissionsCountry.json', 'r') as f:
    co2EmissionsCountry = json.load(f)

annual_average_in_tons = 0
df_pandas = None

app = Flask(__name__, template_folder='./html_files')

spark = SparkSession.builder \
            .master("local") \
            .appName("CarbonFootprintCalculator") \
            .config("spark.driver.extraClassPath", "./drivers/postgresql_42.6.0.jar") \
            .config("spark.jars", "./drivers/postgresql_42.6.0.jar") \
            .getOrCreate()

# Set the location of the session cookie file to a temporary directory
app.config['SESSION_FILE_DIR'] = './'
app.config['SESSION_FILE_THRESHOLD'] = 0
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SECRET_KEY'] = os.urandom(24)

# Main page: if user connected you go to dashboard, otherwise go to login
@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        session.pop('username', None)
        return redirect('/login')

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    country = request.args.get('data')
    return gm(country)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mongo_manager = MongoDBManager('CarbonFootprintCalculator', 'Users')
        if mongo_manager.check_login(username, password):
            session['username'] = username  # Store the username in a session variable
            return redirect('/dashboard')
        else:
            error = "Invalid login credentials. Please try again."  # Set error message, which will appear in the html
    return render_template('login.html', error=error)  # Pass error message to the template

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        mongo_manager = MongoDBManager('CarbonFootprintCalculator', 'Users')

        if mongo_manager.users_collection.find_one({'username': username}): # Username exists -> error
            error = "Username already exists. Please choose a different one."  # Set error message
        elif password != repeat_password:
            error = "Password not matching"
        else: # Create username 
            # Update the user data in the JSON file
            user = {
                'username': username,
                'password': password
            }
            
            mongo_manager.insert_user(user)
            
            session['username'] = username  # Store the username in a session variable
            return redirect('/dashboard')
    return render_template('registration.html', error=error)  # Pass error message to the template

# Page with to access the input, track and recommendations pages
@app.route('/dashboard',  methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect('/logout')

# Questionnaire/Survey page
@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if 'username' not in session: 
        return redirect('/logout')
    
    error = None
    username = session['username']
    airportManager = AirportFootprintManager()
    airport_names = airportManager.list_airport_names()

    if request.method == 'POST':
        date_range_type = request.form.get('date-range')
        start_date = request.form.get('start-date')
        end_date = request.form.get('end-date')

        dates_manager = DatesManager(date_range_type, start_date, end_date)

        start_date = dates_manager.get_start_date()
        end_date = dates_manager.get_end_date()
        number_of_days = dates_manager.get_number_of_days()

        redis_manager = RedisManager('localhost', 6379, 1)


        print("START DATE: ", start_date)
        print("END DATE: ", end_date)
        print("NUMBER OF DAYS: ", number_of_days)
        
        old_start_date = None
        old_end_date = None
        dates_overlap = redis_manager.check_date_overlap(username, start_date, end_date)
        if dates_overlap[0]:
            print("DATES OVERLAP")
            old_start_date = dates_overlap[1]
            old_end_date = dates_overlap[2]
            redis_manager.delete_date_range(username, dates_overlap[1], dates_overlap[2])
        
        print("DATES DO NOT OVERLAP")
        redis_manager.store_date_range(username, start_date, end_date)
        # 1 check if date exists in a range 
        # If exists -> Put an error message and say that in case it exists it will replace the one that is already there
        # If not exists -> All ok, save the range of dates and proceed with the questionnaire
            
        
        response_data = {
            'start_date': start_date,
            'end_date': end_date,
            'number_of_days': int(number_of_days),

            'answerDiet': request.form['diet'],
            'answerWasteFoodPercentage': int(request.form['wastedFoodPercentage']),
            'answerLocalFood': request.form['localFood'],

            'answerCarType': request.form.get('carType', ''),
            'answerCarTime': int(request.form['carTime']) if request.form['carTime'].isdigit() else 0,
            'answerCityBusTime': int(request.form['cityBusTime']) if request.form['cityBusTime'].isdigit() else 0,
            'answerInterCityBusTime': int(request.form['intercityBusTime']) if request.form['intercityBusTime'].isdigit() else 0,
            'answerTrainTime': int(request.form['trainTime']) if request.form['trainTime'].isdigit() else 0,
            'origin_airports': request.form.getlist('origin[]'),
            'destination_airports': request.form.getlist('destination[]'),
            'cabin_classes': request.form.getlist('cabin_class[]'),
            'round_trips': request.form.getlist('round_trip[]'),

            'answerHowManyPeople': request.form['howManyPeople'],
            'anwerHeatingType': request.form['heatingType'],

            'anwerWasteMaterials': request.form.getlist('wasteMaterials[]'),

            'answerShoppingProfile': request.form['shoppingProfile'],
            'answerPhoneLaptop': request.form.getlist('phoneLaptopQuestion[]'),
        }

        postgresql_manager = PostgreSQLManager('localhost',5858,'postgres', 'password', 'mydatabase')
        #  postgresql_manager = PostgreSQLManager('postgres','5432','postgres','password','mydatabase')

        # Retrieve the username from the Flask session
        
        
        # SAVE ANSWERS
        table_name_answers = f'user_{username}_answers'
        
        columns = [
            'start_date DATE',
            'end_date DATE',
            'number_of_days INTEGER',

            'answerDiet VARCHAR(255)',
            'answerWasteFoodPercentage INTEGER',
            'answerLocalFood VARCHAR(255)',

            'answerCarType VARCHAR(255)',
            'answerCarTime INTEGER',
            'answerCityBusTime INTEGER',
            'answerInterCityBusTime INTEGER',
            'answerTrainTime INTEGER',
            'origin_airports VARCHAR(255)[]',
            'destination_airports VARCHAR(255)[]',
            'cabin_classes VARCHAR(255)[]',
            'round_trips VARCHAR(255)[]',

            'answerHowManyPeople VARCHAR(255)',
            'anwerHeatingType VARCHAR(255)',

            'anwerWasteMaterials VARCHAR(255)[]',

            'answerShoppingProfile VARCHAR(255)',
            'answerPhoneLaptop VARCHAR(255)[]'
        ]
        
        postgresql_manager.create_table(table_name_answers, columns)
        postgresql_manager.insert_data(table_name_answers, response_data)


        # SAVE CARBON FOOTPRINT
        carbon_footprint_manager = footprintCalculator(response_data)
        carbon_footprint = carbon_footprint_manager.computeCarbonFootprint()

        table_name_carbon = f'user_{username}_carbon_footprint'
        columns_cf = [
            'start_date DATE',
            'end_date DATE',
            'diet FLOAT',  
            'transportation FLOAT',
            'car FLOAT',
            'bustrain FLOAT',
            'plane FLOAT',
            'housing FLOAT',
            'consumption FLOAT',
            'waste FLOAT',
            'total FLOAT'
        ]
        postgresql_manager.create_table(table_name_carbon, columns_cf)

        postgresql_manager.insert_data(table_name_carbon,carbon_footprint)
        
        if dates_overlap[0]:
            postgresql_manager.delete_table_sample_by_dates(table_name_carbon, old_start_date, old_end_date)


        print(postgresql_manager.get_all_data(table_name_carbon))

        postgresql_manager.close_connection()

        return redirect('/track')
        
    return render_template('input.html', airports=airport_names)

@app.route('/track', methods=['GET', 'POST'])
def track_data():
    if 'username' not in session: 
        return redirect('/logout')
    
    error = None
    graph_data = None
    username = session['username']
    table_name_carbon = f'user_{username}_carbon_footprint'
    redis_manager = RedisManager('localhost', 6379, 0)
    #postgresql_manager = PostgreSQLManager('localhost', 5858, 'postgres', 'password', 'mydatabase')
    graph_creator = graphCreator()

    spark_manager = SparkManager(spark)

    if request.method == 'POST':
        from_date = request.form.get('fromDate')
        to_date = request.form.get('toDate')
        key = str(username) + str(from_date) + str(to_date)
        if from_date > to_date:
            error = "Watch out, the start date is later than the end date!"
        else: 
            if (redis_manager.key_exists_boolean(key)):
                graph_data = redis_manager.get_value_by_key(key)
                return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', error=error)
            else: 
                df = spark_manager.loadDF_with_tablename_and_dates(table_name_carbon, from_date, to_date)
                print("JEJE")
                print(df.show())

                if df:
                    pie_labels = ['diet', 'transportation', 'housing', 'consumption', 'waste']
                    # Calculate the sum of each column for each pie_label
                    sum_values = [F.sum(col).alias(label) for label, col in zip(pie_labels, pie_labels)]
                    result = df.agg(*sum_values)

                    pie_variable_values = list(result.first().asDict().values())

                    print("values: ", pie_variable_values)

                    piefig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_variable_values,hole=0.5)])

                    # Convert the figure to a JSON string
                    pie_graph_data = piefig.to_json()

                    # TODO, store json as a string

                    # Pass the graph data to the HTML template
                    return render_template('track.html', pie_graph_data=pie_graph_data, 
                                           horizontal_bar_data=horizontal_bar_data,
                                           error=error, from_date=from_date, to_date=to_date,
                                           countries = list(co2EmissionsCountry.keys()))
                

                else:
                    error = "No data available for this range of dates"


    from_date, to_date, df = spark_manager.loadDF_with_tablename(table_name_carbon)
    df = df.orderBy("start_date")
    print(df.show())

    # Get the minimum and maximum start dates from the DataFrame
    # Get the minimum and maximum start dates from the DataFrame
    # Get the minimum and maximum start dates from the DataFrame
    min_start_date = df.selectExpr("min(start_date)").first()[0]
    max_start_date = df.selectExpr("max(start_date)").first()[0]

    # Create an empty DataFrame with the same schema as the original DataFrame
    empty_df = spark.createDataFrame([], schema=df.schema)

    # Sort the DataFrame by start_date
    sorted_df = df.orderBy("start_date")

    # Iterate through each row in the sorted DataFrame
    for i in range(sorted_df.count()):
        row = sorted_df.collect()[i]
        start_date = row.start_date
        end_date = row.end_date

        # If it's not the first row, create a row with the start date as the end date of the previous row
        if i > 0:
            prev_row = sorted_df.collect()[i - 1]
            prev_end_date = prev_row.end_date
            missing_start_date = prev_end_date + timedelta(days=1)
            missing_end_date = start_date - timedelta(days=1)
            new_row = (missing_start_date, missing_end_date, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            empty_df = empty_df.union(spark.createDataFrame([new_row], schema=df.schema))

        # Append the original row to the empty DataFrame
        empty_df = empty_df.union(spark.createDataFrame([row], schema=df.schema))

        # If it's the last row, create a row with the end date as the start date of the next row
        if i == sorted_df.count() - 1:
            next_row = sorted_df.collect()[i]
            next_start_date = next_row.start_date
            missing_start_date = end_date + timedelta(days=1)
            missing_end_date = next_start_date - timedelta(days=1)
            new_row = (missing_start_date, missing_end_date, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            empty_df = empty_df.union(spark.createDataFrame([new_row], schema=df.schema))

    # Sort the DataFrame by start_date
    new_df = empty_df.orderBy("start_date")
    new_df = new_df.filter(col("start_date") < col("end_date"))
    new_df = new_df.withColumn("number_of_days", (col("end_date") - col("start_date")).cast("int"))
    new_df = new_df.withColumn("average_per_day", col("total") / col("number_of_days"))

    df = new_df

    # Convert DataFrame to a list of rows
    # Convert DataFrame to a list of rows
    rows = df.collect()

    # Create a new list for updated rows
    updated_rows = []

    # Iterate over each row
    for i in range(len(rows)):
        current_row = rows[i]
        prev_row = rows[i - 1] if i > 0 else None
        next_row = rows[i + 1] if i < len(rows) - 1 else None
        
        # Calculate the new diet value based on the formula
        if current_row["diet"] == 0:
            columns_to_change = ["diet", "transportation", "car", "bustrain", "plane", "housing", "consumption", "waste", "total"]
            updated_row = current_row.asDict()
            for column in columns_to_change:
                if column == "total":
                    updated_row[column] = updated_row["diet"] + updated_row["transportation"] + updated_row["housing"] + updated_row["consumption"] + updated_row["waste"]
                    
                else:
                    prev_value = prev_row[column] if prev_row else 0
                    next_value = next_row[column] if next_row else 0
                    prev_num_days = prev_row["number_of_days"] if prev_row else 0
                    next_num_days = next_row["number_of_days"] if next_row else 0
                    new_value = current_row["number_of_days"] * (prev_value + next_value) / (prev_num_days + next_num_days)
                    
                    # Create a new row with updated diet value
                    updated_row[column] = new_value
                    
            # Append the updated row to the list
            updated_rows.append(updated_row)
        else:
            # Append the original row to the list
            updated_rows.append(current_row.asDict())

    # Create a new DataFrame from the updated list of rows
    df_filled = spark.createDataFrame(updated_rows, df.schema)

    print(df_filled.show())
    df = df_filled

    





    #FILL EMPTY DATES !!!!!!

    
    '''
    if request.method == 'POST':
        from_date = request.form.get('fromDate')
        to_date = request.form.get('toDate')
        key = str(username) + str(from_date) + str(to_date)
        if from_date > to_date:
            error = "Watch out, the start date is later than the end date!"
        else:
            if (redis_manager.key_exists_boolean(key)):
                graph_data = redis_manager.get_value_by_key(key)
                return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', error=error)
            else:
                # Get the data for the current user from the database
                user_data = postgresql_manager.get_data_from_date_range(f'user_{username}', from_date, to_date)

                if user_data:
                    df = pd.DataFrame(user_data, columns=['datetime', 'food', 'transportation', 'household', 'expenses', 'total'])

                    # Create a dictionary to store the data for each date
                    dates = sorted(list(set(df['datetime'])))
                    date_data = {date: {'food': [], 'transportation': [], 'household': [], 'expenses': [], 'total': []} for date in dates}

                    graph_manager = graphCreator(df, dates, date_data)
                    graph_data = graph_manager.create_tracking_graphs()
                    redis_manager.set_key_value(key, graph_data)

                    return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', 
                                           error=error, 
                                           from_date = from_date,
                                           to_date = to_date)
                else:
                    error = "No data available for this range of dates"
    
    # Get the data for the current user from the database
    if df.count() > 0:
        from_date = df.selectExpr('min(start_date) as min_date').first()['min_date']
        to_date = df.selectExpr('max(end_date) as max_date').first()['max_date']

        key = str(username) + str(from_date) + str(to_date)

        if redis_manager.key_exists_boolean(key):
            graph_data = redis_manager.get_value_by_key(key)
            return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}',
                                error=error,
                                from_date=from_date,
                                to_date=to_date)
        else:
            dates = sorted(list(set(df.select(col('start_date')).collect())))
            date_data = {date[0]: {'diet': [], 'transportation': [], 'car': [], 'bustrain': [], 'plane': [], 'housing': [], 'consumption': [], 'waste': [], 'total': []} for date in dates}
            
            graph_manager = graphCreator(df, dates, date_data)
            graph_data = graph_manager.create_tracking_graphs()
            redis_manager.set_key_value(key, graph_data)
    else:
        error = "No data available for this user"
    '''
    # ---------------------------------------------------------------------------------------------------------------------
    # PIE CHART TOTAL
    pie_labels = ['diet', 'transportation', 'housing', 'consumption', 'waste']
    # Calculate the sum of each column for each pie_label
    sum_values = [F.sum(col).alias(label) for label, col in zip(pie_labels, pie_labels)]
    result = df.agg(*sum_values)

    # Retrieve the sum values
    pie_variable_values = list(result.first().asDict().values())
    
    pie_graph_data = graph_creator.create_pie_chart(pie_labels, pie_variable_values)
    
    # ---------------------------------------------------------------------------------------------------------------------
    # Horizontal bars

    #mock data:
    min_start_date = df.select(F.min("start_date")).first()[0]
    max_end_date = df.select(F.max("end_date")).first()[0]
    number_of_days = (max_end_date - min_start_date).days

    total_sum = df.select(F.sum("total")).first()[0]
    global annual_average_in_tons
    annual_average_in_tons = (total_sum/number_of_days)*(365/1000)

    # ---------------------------------------------------------------------------------------------------------------------
    # Data tracking by time
    # Convert the 'start_date' column to datetime and 'total' column to float

    # Create a line time chart plot

    global df_pandas
    df_pandas = df.toPandas()

    # ---------------------------------------------------------------------------------------------------------------------
    # Pass the graph data to the HTML template
    return render_template('track.html', pie_graph_data=pie_graph_data, 
                           graphJSON=gm(),
                           error=error, from_date=from_date, to_date=to_date,
                           time_fig_graph_data=time_graph(),
                           countries = list(co2EmissionsCountry.keys()))

@app.route('/deleteUserData', methods=['GET', 'POST'])
def delete_user_date():
    username = session['username']
    table_name_answers = f'user_{username}_answers'
    table_name_carbon = f'user_{username}_carbon_footprint'
    postgresql_manager = PostgreSQLManager('localhost',5858,'postgres', 'password', 'mydatabase')
    postgresql_manager.delete_all_table_data(table_name_answers)
    postgresql_manager.delete_all_table_data(table_name_carbon)
    postgresql_manager.close_connection()

    return render_template('dashboard.html', username=session['username'])

@app.route('/callbackTime', methods=['POST', 'GET'])
def callback_time():
    data_to_show = request.args.getlist('data')
    data_to_show = data_to_show[0].split(',')
    return time_graph(data_to_show)

def time_graph(y=["diet", "transportation", "housing", "consumption", "waste", "total"]):
    # Plotting the data
    fig = px.line(df_pandas, x="end_date", y=y,
                title='Co2 Over Time')
    
    fig.update_layout(height=500, width=700)

    timegraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    return timegraphJSON



def gm(country='Spain'):
    global_average = 4.5
    global_objective = 0.5
    country_values = co2EmissionsCountry
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=['International', 'Country', 'User Value', 'Global Objective'],
                         x=[global_average, country_values[country], annual_average_in_tons, global_objective],
                         marker=dict(
                            color='rgba(50, 171, 96, 0.6)',
                            line=dict(
                                color='rgba(50, 171, 96, 1.0)',
                                width=1),
                        ),
                         orientation='h'))
    
    fig.update_layout(
            title='CO2 comparison',
            yaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=True,
            ),
            xaxis=dict(
                zeroline=False,
                showline=False,
                showticklabels=True,
                showgrid=True,
                title="Tons of CO2 per capita"
            ),
            legend=dict(
                x=0.029,
                y=1.038,
                font_size=10
            ),
            margin=dict(l=100, r=20, t=70, b=70),
            paper_bgcolor='rgb(248, 248, 255)',
            plot_bgcolor='rgb(248, 248, 255)',
            height=500, 
            width=700
        )

    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON



@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the 'username' key from the session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
