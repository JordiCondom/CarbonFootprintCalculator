import json
import os
from flask import Flask, redirect, render_template, request, session
import numpy as np
import pandas as pd
import plotly
from classes.airportFootprintManager import AirportFootprintManager
from classes.datesManager import DatesManager
from classes.footprintcalculator import footprintCalculator
from classes.graphcreator import graphCreator
from pyspark.sql import SparkSession
import plotly.graph_objects as go
import pyspark.sql.functions as F
import plotly.express as px

from classes.postgresqlmanager import PostgreSQLManager
from classes.recommendationsManager import RecommendationsManager
from classes.redismanager import RedisManager
from classes.sparkmanager import SparkManager

session_cookie_path = './session_cookie'
if os.path.exists(session_cookie_path):
    os.remove('flask_session')

with open('./co2EmissionsCountry.json', 'r') as f:
    co2EmissionsCountry = json.load(f)



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
annual_average_in_tons = 0
df_pandas = None

# Main page: if user connected you go to dashboard, otherwise go to login
@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        session.pop('username', None)
        return redirect('/login')

# Update Horizontal Bar Chart
@app.route('/callback', methods=['POST', 'GET'])
def cb():
    country = request.args.get('data')
    return gm(country)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        redis_manager = RedisManager('localhost', 6379, 2)
        if redis_manager.check_login(request.form['username'], request.form['password']):
            session['username'] = request.form['username']  # Store the username in a session variable
            return redirect('/dashboard')
        else:
            error = "Invalid login credentials. Please try again."  # Set error message, which will appear in the html
    return render_template('login.html', error=error)  

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
            error = "Username already exists. Please choose a different one." 
        elif password != repeat_password: # Passwords not matching -> error
            error = "Password not matching"
        else: # Create username 
            redis_manager.insert_user({
                'id': username,
                'username': username,
                'password': password
            })
            
            session['username'] = username  # Store the username in a session variable
            return redirect('/dashboard')
    return render_template('registration.html', error=error)  # Pass error message to the template

# Main page
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
    
    username = session['username']
    error = None
    redis_manager = RedisManager('localhost', 6379, 1)
    postgresql_manager = PostgreSQLManager('0.0.0.0',5858,'docker', 'docker', 'mydatabase')
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

        if start_date > end_date:
            error = "The end date you have input is before start date, watch out inputting dates!"
            return render_template('input.html', airports=airport_names, error=error)
        
        # Check if data exists for existing dates
        old_start_date = None
        old_end_date = None
        dates_overlap = redis_manager.check_date_overlap(username, start_date, end_date)
        if dates_overlap[0]: # if exists, data gets overwritten
            old_start_date = dates_overlap[1]
            old_end_date = dates_overlap[2]
            redis_manager.delete_date_range(username, dates_overlap[1], dates_overlap[2])
        
        # save dates in redis for further checks
        redis_manager.store_date_range(username, start_date, end_date)
            
        # Collect data of the survery so it can be input in PostgreSQL
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

        # Create answers database (if does not exist) to save the answers
        table_name_answers = f'user_{username}_answers'
        
        # Define columns and types
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

        # Create carbon footprint database (if does not exist) to save carbon footprint data
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
            'shopping_profile FLOAT',
            'refurbished FLOAT',
            'waste FLOAT',
            'plastic FLOAT',
            'glass FLOAT',
            'paper FLOAT',
            'aluminium FLOAT',
            'number_of_days FLOAT',
            'average_per_day FLOAT',
            'total FLOAT'
        ]
        postgresql_manager.create_table(table_name_carbon, columns_cf)
        postgresql_manager.insert_data(table_name_carbon,carbon_footprint)
        
        # If dates overlap, delete the existing data of previous dates
        if dates_overlap[0]:
            postgresql_manager.delete_table_sample_by_dates(table_name_carbon, old_start_date, old_end_date)


        postgresql_manager.close_connection()

        return redirect('/track')
        
    return render_template('input.html', airports=airport_names)

# Page to track the data, get the recommendations and study possible carbon offsetting
@app.route('/track', methods=['GET', 'POST'])
def track_data():
    if 'username' not in session: 
        return redirect('/logout')
    
    error = None
    username = session['username']
    table_name_carbon = f'user_{username}_carbon_footprint'
    graph_creator = graphCreator()
    spark_manager = SparkManager(spark)
    

    # Get the current data on carbon footprint of the user and work with it as an apache spark dataframe 
    try:
        from_date, to_date, df = spark_manager.loadDF_with_tablename(table_name_carbon)
    except:
        error = "No data available to plot"
        return render_template('dashboard.html', error=error)
        
    # Fill data of missing dates in between the dates available
    df = spark_manager.fill_df(df)

    columns_to_sum = ["total", "diet", "transportation", "housing", "consumption", "waste", "car", "bustrain", "plane", "shopping_profile",
                      "refurbished", "plastic", "glass", "paper", "aluminium", "number_of_days"]
    
    # Compute the sum of the specified columns and turn them into a dictionary for further processing
    column_sums = df.select(*columns_to_sum).agg(*[F.sum(col).alias(col) for col in columns_to_sum])
    column_sums_dict = column_sums.first().asDict()

    # ---------------------------------------------------------------------------------------------------------------------
    # Pie chart of all data
    pie_labels = ['Diet', 'Transportation', 'Housing', 'Consumption', 'Waste']
    pie_variable_values = [column_sums_dict['diet'], column_sums_dict['transportation'], column_sums_dict['housing'],column_sums_dict['consumption'],column_sums_dict['waste']]
    pie_graph_data = graph_creator.create_pie_chart(pie_labels, pie_variable_values)
    pie_graph_data_2_trees = graph_creator.create_pie_chart_trees(pie_labels, pie_variable_values)

    # ---------------------------------------------------------------------------------------------------------------------
    #Sunburst chart 

    sun_labels = ["Total","Diet", "Transportation", "Housing", "Consumption", "Waste", "Car", "Public transport", "Plane" ]
    sun_parents = ["","Total", "Total", "Total", "Total", "Total", "Transportation", "Transportation", "Transportation"]


    pie2_variable_values = [column_sums_dict['total'], column_sums_dict['diet'], column_sums_dict['transportation'], column_sums_dict['housing'], column_sums_dict['consumption'],
                            column_sums_dict['waste'], column_sums_dict['car'], column_sums_dict['bustrain'], column_sums_dict['plane']]
    sun_graph_data = graph_creator.create_sun_chart(sun_labels, sun_parents, pie2_variable_values)
    
    # ---------------------------------------------------------------------------------------------------------------------
    # Horizontal bars
    min_start_date = df.select(F.min("start_date")).first()[0]
    max_end_date = df.select(F.max("end_date")).first()[0]
    number_of_days = (max_end_date - min_start_date).days
    global time_dates
    time_dates = pd.date_range(start=min_start_date, end=max_end_date) # all days to plot

    total_sum = column_sums_dict['total']
    global annual_average_in_tons
    annual_average_in_tons = (total_sum/number_of_days)*(365/1000)

    # ---------------------------------------------------------------------------------------------------------------------
    # Data tracking by time
    # Convert the 'start_date' column to datetime and 'total' column to float

    # Create a line time chart plot

    selected_columns = ["end_date","diet", "transportation", "housing", "consumption", "waste", "total", "number_of_days"]
    
    local_df_pandas = df.toPandas()[selected_columns]

    new_df = local_df_pandas.copy()

    # Process to create dataframe where each row is a day of input data and the respective averaged value
    # Initialize an empty list to store the exploded rows
    exploded_rows = []

    # Iterate over each row in the DataFrame
    for index, row in local_df_pandas.iterrows():
        # Get the number of days for the current row
        num_days = int(row['number_of_days'])
        
        # Divide the values of selected columns by the number of days
        divided_values = row[selected_columns[1:]].div(num_days)
        
        # Create new rows by repeating the divided values
        exploded = divided_values.explode().to_frame().T
        
        # Append the exploded rows to the list
        for _ in range(num_days):
            exploded_rows.append(exploded)
        
    # Concatenate the exploded rows to create the new DataFrame
    new_df = pd.concat(exploded_rows).reset_index(drop=True)

    global df_pandas
    df_pandas = new_df

    # ---------------------------------------------------------------------------------------------------------------------
    # Recommendations
    recommendations_manager = RecommendationsManager(column_sums_dict)
    recommendations_vector = recommendations_manager.generate_recommendations(df.count())


    return render_template('track.html', pie_graph_data=pie_graph_data, 
                           graphJSON=gm(),
                           sun_graph_data=sun_graph_data,
                           error=error, from_date=min_start_date, to_date=max_end_date,
                           time_fig_graph_data=time_graph(),
                           countries = list(co2EmissionsCountry.keys()),
                           recommendations_vector=recommendations_vector,
                           pie_graph_data_2_trees=pie_graph_data_2_trees)

# Delete connected user data
@app.route('/deleteUserData', methods=['GET', 'POST'])
def delete_user_date():
    username = session['username']
    table_name_answers = f'user_{username}_answers'
    table_name_carbon = f'user_{username}_carbon_footprint'
    postgresql_manager = PostgreSQLManager('0.0.0.0',5858,'docker', 'docker', 'mydatabase')
    redis_manager = RedisManager('localhost', 6379, 1)

    redis_manager.delete_user_data(username)
    postgresql_manager.delete_all_table_data(table_name_answers)
    postgresql_manager.delete_all_table_data(table_name_carbon)
    postgresql_manager.close_connection()

    return render_template('dashboard.html', username=session['username'])

# Callback to update plot to track data in time
@app.route('/callbackTime', methods=['POST', 'GET'])
def callback_time():
    data_to_show = request.args.getlist('data')
    data_to_show = data_to_show[0].split(',')
    return time_graph(data_to_show)

# Create plot to track data in time
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

    dates = time_dates[:df_pandas.shape[0]]

    fig = px.line(df_pandas, x=dates, y=y, color_discrete_map=color_map,
                title='Co2 Over Time')
    

    
    fig.update_layout(height=500, width=700)

    timegraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    return timegraphJSON

# Create horizontal barchart
def gm(country='Afghanistan'):
    global_average = 4.8
    country_values = co2EmissionsCountry
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=['Worldwide CF per capita', 'Country CF per capita', 'Your average CF', 'Global Objective'],
                         x=[global_average, country_values[country], annual_average_in_tons, 0.8*country_values[country]],
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

# logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the 'username' key from the session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
