import base64
import io
import json
import os
from datetime import datetime
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

from classes.postgresqlmanager import PostgreSQLManager
from classes.redismanager import RedisManager
from classes.sparkmanager import SparkManager

session_cookie_path = './session_cookie'
if os.path.exists(session_cookie_path):
    os.remove('flask_session')

with open('./co2EmissionsCountry.json', 'r') as f:
    co2EmissionsCountry = json.load(f)

annual_average_in_tons = 0

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

       # Example usage

        # Convert start_date and end_date to range_start and range_end as timestamps
        range_start = time.mktime(start_date.timetuple())
        range_end = time.mktime(end_date.timetuple())

        overlapping_ranges = redis_manager.dates_overlap(range_start, range_end)
        if overlapping_ranges:
            for overlapping_range in overlapping_ranges:
                range_id = redis_manager.get_value_by_key(overlapping_range.decode())
                error = f"New range of dates overlaps with existing range {range_id}"
                # Handle the error message
        else:
            # Insert the range into Redis since there are no overlapping ranges
            range_id = str(username) + str(start_date) + str(end_date)
            redis_manager.insert_range_dates(range_start, range_end, range_id)
            
            
        
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
    print(df.show())

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
    # PIE CHART
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
    """
    country_average = 0.2
    global_average = 4.5
    global_objective = 0.5



    x = [annual_average_in_tons, country_average, global_average, global_objective]
    y = ["annual_average_in_tons", "country_average", "global_average", "global_objective"]

    horizontal_bar_data = graph_creator.create_horizontal_bars(x,y)
    """

    # Pass the graph data to the HTML template
    return render_template('track.html', pie_graph_data=pie_graph_data, 
                           graphJSON=gm(),
                           error=error, from_date=from_date, to_date=to_date,
                           countries = list(co2EmissionsCountry.keys()))




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
