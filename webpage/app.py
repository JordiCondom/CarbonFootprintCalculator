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
        redis_manager = RedisManager('localhost', 6379, 2)
        if redis_manager.check_login(username, password):
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
        redis_manager = RedisManager('localhost', 6379, 2)

        if redis_manager.check_username_exists(username): # Username exists -> error
            error = "Username already exists. Please choose a different one."  # Set error message
        elif password != repeat_password:
            error = "Password not matching"
        else: # Create username 
            # Update the user data in the JSON file
            user = {
                'id': username,
                'username': username,
                'password': password
            }
            
            redis_manager.insert_user(user)
            
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
        
        old_start_date = None
        old_end_date = None
        dates_overlap = redis_manager.check_date_overlap(username, start_date, end_date)
        if dates_overlap[0]:
            old_start_date = dates_overlap[1]
            old_end_date = dates_overlap[2]
            redis_manager.delete_date_range(username, dates_overlap[1], dates_overlap[2])
        
        redis_manager.store_date_range(username, start_date, end_date)
        # 1 check if date exists in a range 
        # If exists -> Put an error message and say that in case it exists it will replace the one that is already there
        # If not exists -> All ok, save the range of dates and proceed with the questionnaire
            
        
        response_data = {
            'start_date': start_date,
            'end_date': end_date,
            'number_of_days': int(number_of_days),

            'answerDiet': request.form['diet'],
            'answerWasteFoodPercentage': int(request.form['wastedFoodPercentage']) if request.form['wastedFoodPercentage'].isdigit() else 5,
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
            'number_of_days FLOAT',
            'average_per_day FLOAT',
            'total FLOAT'
        ]
        postgresql_manager.create_table(table_name_carbon, columns_cf)

        postgresql_manager.insert_data(table_name_carbon,carbon_footprint)
        
        if dates_overlap[0]:
            postgresql_manager.delete_table_sample_by_dates(table_name_carbon, old_start_date, old_end_date)

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
                print(df.show())

                if df:
                    pie_labels = ['diet', 'transportation', 'housing', 'consumption', 'waste']
                    # Calculate the sum of each column for each pie_label
                    sum_values = [F.sum(col).alias(label) for label, col in zip(pie_labels, pie_labels)]
                    result = df.agg(*sum_values)

                    pie_variable_values = list(result.first().asDict().values())

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
    print(df.show())
    df = spark_manager.fill_df(df)

    # ---------------------------------------------------------------------------------------------------------------------
    # PIE CHART TOTAL
    pie_labels = ['diet', 'transportation', 'housing', 'consumption', 'waste']
    # Calculate the sum of each column for each pie_label
    sum_values = [F.sum(col).alias(label) for label, col in zip(pie_labels, pie_labels)]
    result = df.agg(*sum_values)

    # Retrieve the sum values
    pie_variable_values = list(result.first().asDict().values())
    
    pie_graph_data = graph_creator.create_pie_chart(pie_labels, pie_variable_values)
    pie_graph_data_2_trees = graph_creator.create_pie_chart_trees(pie_labels, pie_variable_values)

    # ---------------------------------------------------------------------------------------------------------------------
    #SUNBURST!!! 

    sun_labels = ["total","diet", "transportation", "housing", "consumption", "waste", "car", "bustrain", "plane" ]
    sun_parents = ["","total", "total", "total", "total", "total", "transportation", "transportation", "transportation"]
    sun_values = [F.sum(col).alias(label) for label, col in zip(sun_labels, sun_labels)]
    result2 = df.agg(*sun_values)

    pie2_variable_values = list(result2.first().asDict().values())
    sun_graph_data = graph_creator.create_sun_chart(sun_labels, sun_parents, pie2_variable_values)
    
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
    # Recommendations
    recommendations_vector = ["Eat less meat Eat less meat Eat less meat Eat less meat Eat less meat", "Use your car less", "Use more public transport", "Don't consume that much", "Recycle more"]

    return render_template('track.html', pie_graph_data=pie_graph_data, 
                           graphJSON=gm(),
                           sun_graph_data=sun_graph_data,
                           error=error, from_date=from_date, to_date=to_date,
                           time_fig_graph_data=time_graph(),
                           countries = list(co2EmissionsCountry.keys()),
                           recommendations_vector=recommendations_vector,
                           pie_graph_data_2_trees=pie_graph_data_2_trees)

@app.route('/deleteUserData', methods=['GET', 'POST'])
def delete_user_date():
    username = session['username']
    table_name_answers = f'user_{username}_answers'
    table_name_carbon = f'user_{username}_carbon_footprint'
    postgresql_manager = PostgreSQLManager('localhost',5858,'postgres', 'password', 'mydatabase')
    redis_manager = RedisManager('localhost', 6379, 1)

    redis_manager.delete_user_data(username)
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
    if y == ['']:
        # Return an empty plot
        return "{}"

    color_map = {
        "diet": "red",
        "transportation": "blue",
        "housing": "green",
        "consumption": "orange",
        "waste": "purple",
        "total": "gray"
    }

    fig = px.line(df_pandas, x="end_date", y=y, color_discrete_map=color_map,
                title='Co2 Over Time')
    
    fig.update_layout(height=500, width=700)

    timegraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    return timegraphJSON


def gm(country='Afghanistan'):
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
